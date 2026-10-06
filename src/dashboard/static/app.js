'use strict';
const $ = (selector, root = document) => root.querySelector(selector);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const text = value => typeof value === 'string' ? value : value == null ? '' : JSON.stringify(value);
const array = value => Array.isArray(value) ? value : [];
const state = {projects:[], project:null, id:'', view:'overview', fingerprint:'', search:'', mediaType:'all', mediaRole:'all', shotFilter:'', entityFilter:'', relationShot:'', busy:false, modal:null};
const labels = {storyboard:'Storyboard',image:'Image',video:'Vidéo',audio:'Audio',shot:'Rendu de plan',reference:'Référence',unlinked:'Non relié',character:'Personnage',location:'Lieu',prop:'Accessoire',present:'Présent',missing:'À préparer',invalid:'À vérifier',not_applicable:'Non requis'};
const short = (value, length=110) => { const t=text(value); return t.length>length ? t.slice(0,length-1)+'…' : t; };
const displayId = id => text(id).replaceAll('_',' ');
const mediaById = id => array(state.project?.media).find(m=>m.id===id);
const mediaUrl = m => {
  const u = text(m?.url);
  return u.startsWith('/media/') && !/[\u0000-\u001f]/.test(u) ? u : '';
};
const imagesFor = ids => array(ids).map(mediaById).filter(m=>m?.kind==='image');
const belongsToShot = (m, shot) => !!shot && (array(m.shot_ids).includes(shot.id) || array(shot.media_ids).includes(m.id));
const inputUsesFor = (m, shot) => array(m.usage_records).filter(r=>shot && array(r.shot_ids).includes(shot.id));
const touchesShot = (m, shot) => belongsToShot(m,shot) || inputUsesFor(m,shot).length>0;
const belongsToEntity = (m, entity) => !!entity && (array(m.entity_ids).includes(entity.id) || array(entity.media_ids).includes(m.id));
const shotMedia = shot => array(state.project?.media).filter(m=>belongsToShot(m,shot));
const shotEntities = shot => array(state.project?.entities).filter(e=>array(shot.characters).includes(e.id)||array(shot.props).includes(e.id)||shot.location_id===e.id);
const shotReferences = shot => array(state.project?.media).filter(m=>inputUsesFor(m,shot).length>0 || m.role==='reference'&&(belongsToShot(m,shot)||shotEntities(shot).some(e=>belongsToEntity(m,e))));
const shotImages = shot => shotMedia(shot).filter(m=>m.kind==='image' && m.role!=='reference' && m.role!=='storyboard' && !m.archived).sort((a,b)=>(b.modified_at||0)-(a.modified_at||0));
const titleOf = item => text(item?.title || item?.name || item?.id || 'Sans titre');
const empty = (title, description, icon='◈') => `<div class="empty"><span class="empty-symbol">${esc(icon)}</span><h3>${esc(title)}</h3><p>${esc(description)}</p></div>`;
const heading = (eyebrow,title,description) => `<div class="page-heading"><div><div class="eyebrow">${esc(eyebrow)}</div><h1 class="page-title">${esc(title)}</h1><p class="intro">${esc(description)}</p></div></div>`;
const badge = (label, style='') => `<span class="badge ${esc(style)}">${esc(label)}</span>`;
const relationKind = m => m.relation==='explicit'?'explicit':m.relation==='filename'?'filename':'unknown';
const relationBadge = m => badge(relationKind(m)==='explicit'?'Lien documenté':relationKind(m)==='filename'?'Lien par nom de fichier':'Origine du lien inconnue',relationKind(m)==='explicit'?'good':relationKind(m)==='filename'?'warn':'');
const inputRelation = (m, shot) => inputUsesFor(m,shot).length ? {relation:'explicit'} : m;
function modalItem(kind,id){return kind==='media'?mediaById(id):array(state.project?.[{shot:'shots',entity:'entities',artifact:'artifacts',panel:'panels'}[kind]]).find(x=>(kind==='artifact'?x.path:x.id)===id);}
function resetSelection(){state.shotFilter='';state.entityFilter='';state.relationShot='';state.search='';state.fingerprint='';closeModal();}
function reviewBadges(m){
  const status=m.review_status || m.visual_review_status || m.asset_status || m.status;
  return `${m.archived?badge('ARCHIVÉ / REMPLACÉ','warn'):''}${status?badge(short(status,90)):''}${m.approved===true?badge('Asset approuvé','good'):m.approved===false?badge('Asset non approuvé','warn'):badge('Approbation asset non renseignée')}${m.identity_approved===true?badge('Identité approuvée','good'):m.identity_approved===false?badge('Identité non approuvée','warn'):''}${m.production_final===true?badge('Final production documenté','good'):''}${m.film_final===true?badge('Final film documenté','good'):''}`;
}
const formatDate = value => { if(!value)return 'Date inconnue'; const d=new Date(typeof value==='number' && value<1e12 ? value*1000 : value); return Number.isNaN(d.getTime()) ? 'Date inconnue' : d.toLocaleString('fr-FR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}); };
const img = (media, alt='', cls='') => mediaUrl(media) ? `<img src="${esc(mediaUrl(media))}" alt="${esc(alt)}" class="${esc(cls)}" loading="lazy">` : '';

/* ---------- Readable names ---------- */
const pad2 = n => String(n).padStart(2,'0');
const isHashName = name => /^[0-9a-f]{6,}_\d+\.[a-z0-9]+$/i.test(name);
function mediaLabel(m){
  const parts=text(m?.path).split('/');const name=parts.pop()||'';const base=name.replace(/\.[^.]+$/,'');
  if(parts.at(-1)==='crops'){parts.pop();return `${parts.slice(-2).join(' · ')} · ${base.replaceAll('-',' ')}`;}
  if(isHashName(name))return parts.slice(-2).join(' · ')||name;
  return base;
}
const sceneOf = shot => array(state.project?.scenes).find(c=>c.id===shot?.scene_id||array(c.shot_ids).includes(shot?.id));
function shotLabel(shot){
  const scene=sceneOf(shot);const index=array(state.project?.shots).indexOf(shot)+1;
  const number=Number.isInteger(shot?.sequence)?shot.sequence:index;
  return `${Number.isInteger(scene?.number)?`S${pad2(scene.number)} · `:''}P${pad2(number)}`;
}
const timecode = seconds => { const s=Math.max(0,Math.round(Number(seconds)||0)); return `${Math.floor(s/60)}:${pad2(s%60)}`; };
const money = value => typeof value==='number' && Number.isFinite(value) ? `${value.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:3})} $` : 'Inconnu';

/* ---------- Production model (derived only from catalogue data) ---------- */
const PHASES = [['writing','Écriture'],['world','Monde & style'],['cutting','Découpage'],['images','Images clés'],['motion','Animation'],['finishing','Finition']];
const nextStage = () => array(state.project?.stages).find(s=>s.id!=='project' && s.status!=='present');
const isRejected = m => /reject|rejet|refus|blocked|bloqu/i.test(`${m.review_status||''} ${m.status||''}`);
const promptsOf = (shot, kind) => array(shot.prompts).filter(a=>(typeof a==='object'?a.kind:'')===kind);
function shotProgress(shot){
  const keyframes=shotImages(shot);const media=shotMedia(shot).filter(m=>m.role!=='reference'&&!m.archived);
  const videos=media.filter(m=>m.kind==='video');const audio=media.filter(m=>m.kind==='audio');
  const visual=list=>!list.length?'todo':list.some(m=>m.approved===true)?'done':list.every(isRejected)?'bad':'have';
  return {
    image_prompt: promptsOf(shot,'image_prompt').length?'have':'todo',
    keyframe: visual(keyframes),
    video_prompt: shot.needs_motion===false?'na':promptsOf(shot,'video_prompt').length?'have':'todo',
    video: shot.needs_motion===false?'na':visual(videos),
    audio: audio.length?'have':promptsOf(shot,'audio_prompt').length?'prompt':'todo',
    counts:{keyframes:keyframes.length,videos:videos.length},
  };
}
const CELL = {done:['✓','Approuvé'],have:['●','Présent'],prompt:['◐','Prompt seulement'],bad:['✕','Rejeté / bloqué'],todo:['—','À faire'],na:['·','Non requis']};
const cell = (state_, detail='') => `<span class="cell cell-${esc(state_)}" title="${esc(CELL[state_][1])}">${CELL[state_][0]}${detail?` <small>${esc(detail)}</small>`:''}</span>`;

function tracker(compact=false){
  const stages=array(state.project.stages);const next=nextStage();
  const presentCount=stages.filter(s=>s.status==='present').length;
  const columns=PHASES.map(([id,label])=>{const rows=stages.filter(s=>(s.phase||'')===id);if(!rows.length)return '';
    const done=rows.filter(s=>s.status==='present').length;
    return `<div class="phase ${done===rows.length?'phase-done':done?'phase-active':''}"><div class="phase-head"><span>${esc(label)}</span><small>${done}/${rows.length}</small></div>${rows.map(s=>`<div class="phase-row ${esc(s.status)} ${next&&next.id===s.id?'is-next':''}"><i></i><span>${esc(s.label)}</span><small>${s.status==='present'?esc(s.count)+(s.documented_approvals!=null?` · ${esc(s.documented_approvals)} ✓`:''):s.status==='invalid'?'à vérifier':next&&next.id===s.id?'prochaine':''}</small></div>`).join('')}</div>`;}).join('');
  return `<div class="tracker ${compact?'compact':''}">${columns}</div><p class="relation-note">${presentCount}/${stages.length} étapes ont des fichiers. « ✓ » = approbations documentées dans un registre. La présence d’un fichier ne vaut pas validation.</p>`;
}
function nextStageCallout(){
  const next=nextStage();
  return next?`<div class="next-step"><span class="eyebrow">PROCHAINE ÉTAPE</span><strong>${esc(next.label)}</strong><p>Première étape de la méthode sans fichier dans le projet.</p></div>`:`<div class="next-step"><span class="eyebrow">TOUTES LES ÉTAPES ONT DES FICHIERS</span><strong>Revue finale</strong><p>Présence ≠ validation : vérifie les approbations.</p></div>`;
}
function budgetPanel(){
  const b=state.project.budget;const d=b?.decision&&typeof b.decision==='object'?b.decision:null;const l=b?.ledger;
  const ceiling=typeof d?.max_spend_usd==='number'?d.max_spend_usd:null;const committed=l?.committed_usd;
  const pct=ceiling&&typeof committed==='number'?Math.min(100,committed/ceiling*100):0;
  return `<section class="panel budget-panel"><h3>Budget</h3>${!b?'<p class="intro">Aucun document budgétaire.</p>':`
    <div class="budget-row"><span>Gamme retenue</span><b>${esc(d?.selected_tier||'Non renseignée')}</b></div>
    <div class="budget-row"><span>Plafond de planification</span><b>${ceiling!=null?money(ceiling):'Non renseigné'}</b></div>
    <div class="budget-row"><span>Engagé (registre)</span><b>${l?.available?money(committed):'Inconnu'}</b></div>
    ${l?.available?`<div class="budget-row"><span>Jobs enregistrés</span><b>${esc(l.jobs)}${l.jobs_without_actual_cost?` · ${esc(l.jobs_without_actual_cost)} sans coût réel`:''}</b></div>`:''}
    ${ceiling&&typeof committed==='number'?`<div class="progress-track budget-track"><i style="width:${pct.toFixed(1)}%"></i></div><p class="relation-note">${pct.toFixed(1)} % du plafond engagé.</p>`:''}
    <p class="relation-note">Le plafond encadre la planification ; chaque génération payante demande un accord séparé. Un coût inconnu n’est jamais compté comme nul.</p>`}</section>`;
}

/* ---------- Visual bible ---------- */
function entityRefs(entity){return array(state.project.media).filter(m=>m.kind==='image'&&!m.archived&&belongsToEntity(m,entity));}
function entitySummary(entity){
  const refs=entityRefs(entity);const sheets=refs.filter(m=>!m.derived_from);
  const approved=sheets.filter(m=>array(m.reference_approvals).length).sort((a,b)=>Math.max(...b.reference_approvals.map(r=>r.order??0))-Math.max(...a.reference_approvals.map(r=>r.order??0)));
  const cover=approved[0]||sheets.sort((a,b)=>(b.modified_at||0)-(a.modified_at||0))[0]||refs[0];
  return {refs,sheets,approved,cover,views:refs.length-sheets.length};
}
function bibleCard(entity){
  const s=entitySummary(entity);
  const status=s.approved.length?badge(`${s.approved.length} approuvée${s.approved.length>1?'s':''} au registre`,'good'):s.sheets.length?badge('Candidates à revoir','warn'):badge('Aucune référence');
  return `<button class="bible-card" data-action="entity" data-id="${esc(entity.id)}"><div class="visual">${s.cover?img(s.cover,titleOf(entity)):`<div class="visual-placeholder">${esc(entity.kind==='location'?'⌂':'◯')}</div>`}<span class="tag">${esc(labels[entity.kind]||entity.kind)}</span></div><div class="card-body"><div class="card-label">${esc(entity.id)}</div><h3 class="card-title">${esc(titleOf(entity))}</h3><div class="card-bottom"><span>${status}</span><span class="dim">${s.sheets.length} planche${s.sheets.length>1?'s':''} · ${s.views} vue${s.views>1?'s':''}</span></div></div></button>`;
}
function bibleSection(){
  const entities=array(state.project.entities);
  if(!entities.length)return empty('La bible visuelle est vide','Les personnages, lieux et accessoires apparaîtront dès qu’ils seront déclarés dans le projet.','◯');
  return `<div class="grid bible-grid">${entities.map(bibleCard).join('')}</div>`;
}

/* ---------- Timeline & shot board ---------- */
function orderedShots(){
  let cursor=0;
  return array(state.project.shots).map((shot,i)=>({shot,i})).sort((a,b)=>(a.shot.start_seconds??Infinity)-(b.shot.start_seconds??Infinity)||(a.shot.sequence??a.i)-(b.shot.sequence??b.i)).map(({shot})=>{
    const start=typeof shot.start_seconds==='number'?shot.start_seconds:cursor;const duration=typeof shot.duration_seconds==='number'&&shot.duration_seconds>0?shot.duration_seconds:null;
    cursor=start+(duration||0);return {shot,start,duration};
  });
}
function timeline(){
  const rows=orderedShots();const target=Number(state.project.duration_seconds)||0;
  const total=Math.max(target,...rows.map(r=>r.start+(r.duration||2)),1);const scale=7;const width=Math.max(900,Math.round(total*scale));
  const ticks=[];for(let t=0;t<=total;t+=total>600?60:30)ticks.push(`<span class="tick" style="left:${(t*scale).toFixed(0)}px">${timecode(t)}</span>`);
  if(!rows.length)return `<div class="timeline-scroll"><div class="timeline" style="width:${width}px"><div class="ruler">${ticks.join('')}</div><div class="timeline-empty">${target?`Durée cible ${timecode(target)} — `:''}le découpage en plans n’existe pas encore. La timeline se remplira automatiquement avec les plans.</div></div></div>`;
  const scenes=[];for(const r of rows){const id=r.shot.scene_id||'—';const last=scenes.at(-1);if(last&&last.id===id)last.end=r.start+(r.duration||2);else scenes.push({id,start:r.start,end:r.start+(r.duration||2)});}
  const sceneBand=scenes.map(s=>{const scene=array(state.project.scenes).find(c=>c.id===s.id);return `<span class="scene-span" style="left:${(s.start*scale).toFixed(0)}px;width:${Math.max(4,(s.end-s.start)*scale-2).toFixed(0)}px">${esc(Number.isInteger(scene?.number)?`Scène ${scene.number}`:short(scene?titleOf(scene):s.id,40))}</span>`;}).join('');
  const segments=rows.map(({shot,start,duration})=>{const p=shotProgress(shot);const thumb=shotImages(shot)[0];
    return `<button class="segment seg-${esc(p.keyframe)} ${duration?'':'seg-unknown'}" data-action="shot" data-id="${esc(shot.id)}" style="left:${(start*scale).toFixed(0)}px;width:${Math.max(6,(duration||2)*scale-2).toFixed(0)}px" title="${esc(shotLabel(shot))} · ${esc(titleOf(shot))}${duration?` · ${duration} s`:' · durée inconnue'}">${thumb?img(thumb,''):''}<span>${esc(shotLabel(shot))}</span></button>`;}).join('');
  return `<div class="timeline-scroll"><div class="timeline" style="width:${width}px"><div class="ruler">${ticks.join('')}</div><div class="scene-band">${sceneBand}</div><div class="segments">${segments}</div>${target?`<i class="target-mark" style="left:${(target*scale).toFixed(0)}px" title="Durée cible"></i>`:''}</div></div><div class="legend timeline-legend"><span><i class="sw seg-done"></i>Keyframe approuvée</span><span><i class="sw seg-have"></i>Keyframe candidate</span><span><i class="sw seg-bad"></i>Rejetée</span><span><i class="sw seg-todo"></i>Sans keyframe</span></div>`;
}
function shotBoard(){
  const rows=orderedShots();if(!rows.length)return '';
  const progress=rows.map(r=>({...r,p:shotProgress(r.shot)}));const n=rows.length;
  const total=key=>progress.filter(r=>['done','have'].includes(r.p[key])).length;
  const applicable=key=>progress.filter(r=>r.p[key]!=='na').length;
  const head=[['image_prompt','Prompt image'],['keyframe','Keyframe'],['video_prompt','Prompt vidéo'],['video','Vidéo'],['audio','Son']];
  let lastScene=null;
  const body=progress.map(({shot,duration,p})=>{let sep='';if(shot.scene_id!==lastScene){lastScene=shot.scene_id;const scene=sceneOf(shot);sep=`<tr class="scene-row"><td colspan="7">${esc(scene?titleOf(scene):'Scène non documentée')}</td></tr>`;}
    const thumb=shotImages(shot)[0];
    return sep+`<tr data-action="shot" data-id="${esc(shot.id)}" tabindex="0"><td class="shot-cell">${thumb?img(thumb,''):'<span class="thumb-empty"></span>'}<span><b>${esc(shotLabel(shot))}</b><small>${esc(short(titleOf(shot),70))}</small></span></td><td class="mono">${duration?`${esc(duration)} s`:'—'}</td><td>${cell(p.image_prompt)}</td><td>${cell(p.keyframe,p.counts.keyframes>1?`×${p.counts.keyframes}`:'')}</td><td>${cell(p.video_prompt)}</td><td>${cell(p.video,p.counts.videos>1?`×${p.counts.videos}`:'')}</td><td>${cell(p.audio)}</td></tr>`;}).join('');
  return `<div class="board-summary">${head.map(([k,l])=>{const a=applicable(k);const v=total(k);return `<div><span>${esc(l)}</span><b>${v}<small>/${a}</small></b><div class="progress-track"><i style="width:${a?(v/a*100).toFixed(0):0}%"></i></div></div>`;}).join('')}</div>
  <div class="board-scroll"><table class="board"><thead><tr><th>Plan</th><th>Durée</th>${head.map(([,l])=>`<th>${esc(l)}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></div>
  <div class="legend">${Object.entries(CELL).map(([k,[s,l]])=>`<span>${cell(k)} ${esc(l)}</span>`).join('')}</div><p class="relation-note">Sur ${n} plans. « Présent » signifie qu’un fichier existe ; seule une approbation documentée affiche ✓.</p>`;
}
/* ---------- Storyboard ---------- */
function panelCard(panel,index=0){
  const frame=array(panel.media_ids).map(mediaById).find(m=>m?.kind==='image');const shot=array(state.project.shots).find(s=>s.id===panel.shot_id);
  return `<button class="panel-card" data-action="panel" data-id="${esc(panel.id)}"><div class="panel-frame">${frame?img(frame,''):`<div class="panel-sketch"><span>${esc(short(panel.composition||panel.action||'Cadre à dessiner',150))}</span></div>`}<span class="panel-number">${pad2(panel.order||index+1)}</span>${panel.duration_seconds?`<span class="duration">${esc(panel.duration_seconds)} s</span>`:''}</div><div class="panel-caption"><div class="card-label">${esc(shot?shotLabel(shot):panel.shot_id||panel.id)}</div>${panel.camera?`<p class="panel-camera">CAM · ${esc(short(panel.camera,90))}</p>`:''}<p class="card-description">${esc(short(panel.action||panel.title||'',170))}</p></div></button>`;
}
function sceneBrief(scene){
  return `<div class="scene-brief">${scene.visual_intent?`<div><span class="eyebrow">INTENTION VISUELLE</span><p>${esc(short(scene.visual_intent,420))}</p></div>`:''}${scene.audio_intent?`<div><span class="eyebrow">INTENTION SONORE</span><p>${esc(short(scene.audio_intent,300))}</p></div>`:''}${!scene.visual_intent&&!scene.audio_intent?`<p class="intro">${esc(short(scene.description||'Aucune intention renseignée.',300))}</p>`:''}</div>`;
}
function storyboardView(){
  const p=state.project;const scenes=array(p.scenes);const panels=array(p.panels);
  let html=heading('STORYBOARD','Le film, case par case.','Chaque scène du scénario et ses cases dessinées : cadrage, caméra, action, rythme. Les cases s’ajoutent ici dès que le storyboard existe.');
  if(!scenes.length&&!panels.length)return html+empty('Pas encore de scénario ni de storyboard','Le storyboard apparaîtra à partir des scènes du scénario.','▥');
  const drawn=panels.filter(x=>array(x.media_ids).some(id=>mediaById(id)?.kind==='image')).length;
  const covered=scenes.filter(c=>panels.some(x=>x.scene_id===c.id)).length;
  html+=`<div class="board-summary storyboard-summary"><div><span>Scènes</span><b>${covered}<small>/${scenes.length} avec storyboard</small></b></div><div><span>Cases</span><b>${panels.length}</b></div><div><span>Cases dessinées</span><b>${drawn}<small>/${panels.length}</small></b></div><div><span>Durée découpée</span><b>${timecode(panels.reduce((t,x)=>t+(Number(x.duration_seconds)||0),0))}</b></div></div>`;
  html+=scenes.map((scene,i)=>{const own=panels.filter(x=>x.scene_id===scene.id);const characters=array(p.entities).filter(e=>array(scene.characters).includes(e.id)||scene.location_id===e.id);
    return `<section class="storyboard-scene"><div class="scene-head"><span class="scene-number">${pad2(scene.number??i+1)}</span><div><div class="card-label">${esc(scene.id)}${scene.time?` · ${esc(scene.time)}`:''}</div><h2>${esc(titleOf(scene))}</h2></div><span class="scene-count">${own.length?`${own.length} CASE${own.length>1?'S':''}`:'STORYBOARD À FAIRE'}</span></div>
    ${characters.length?`<div class="entity-list">${characters.map(entityPill).join('')}</div>`:''}
    ${own.length?`<div class="storyboard-grid">${own.map(panelCard).join('')}</div>`:`${sceneBrief(scene)}<div class="storyboard-grid">${[1,2,3].map(n=>`<div class="panel-card placeholder"><div class="panel-frame"><div class="panel-sketch"><span>Case ${n}</span></div></div></div>`).join('')}</div>`}
    ${array(scene.notes).length?`<div class="document-list scene-notes">${scene.notes.map(n=>`<button class="document-row" data-action="artifact" data-id="${esc(n)}"><b>${esc(n)}</b><span>Lire la scène ↗</span></button>`).join('')}</div>`:''}</section>`;}).join('');
  const orphan=panels.filter(x=>!scenes.some(c=>c.id===x.scene_id));
  if(orphan.length)html+=`<div class="section-heading"><h2>Cases sans scène documentée</h2></div><div class="storyboard-grid">${orphan.map(panelCard).join('')}</div>`;
  return html;
}
function productionView(){
  const p=state.project;const shots=array(p.shots);
  return heading('SUIVI DE PRODUCTION','Où en est le film ?','L’avancement réel, plan par plan, calculé à partir des fichiers du projet. Lecture seule.')
  +`<div class="production-top">${nextStageCallout()}${budgetPanel()}</div>
  <div class="section-heading"><div><h2>Le parcours</h2><small>MÉTHODE : ÉCRITURE → MONDE → DÉCOUPAGE → IMAGES → ANIMATION → FINITION</small></div></div>${tracker()}
  <div class="section-heading"><div><h2>Timeline du film</h2><small>${shots.length?`${shots.length} PLANS · ${timecode(orderedShots().reduce((t,r)=>t+(r.duration||0),0))}`:'EN ATTENTE DU DÉCOUPAGE'}${p.duration_seconds?` · CIBLE ${timecode(p.duration_seconds)}`:''}</small></div></div>${timeline()}
  ${shots.length?`<div class="section-heading"><div><h2>Tableau des plans</h2><small>CHAQUE LIGNE OUVRE LE PLAN</small></div></div>${shotBoard()}`:''}
  <div class="section-heading"><div><h2>Bible visuelle</h2><small>PLANCHES DE RÉFÉRENCE PAR PERSONNAGE, LIEU ET ACCESSOIRE</small></div></div>${bibleSection()}`;
}
async function getJSON(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error(`Le serveur a répondu ${r.status}.`);return r.json();}
async function refresh(force=false){
  if(state.busy)return; state.busy=true;
  try{
    const result=await getJSON('/api/projects');state.projects=array(result.projects);
    const params=new URLSearchParams(location.search); const wanted=state.id||params.get('project');
    if(!state.projects.some(p=>p.id===wanted)){state.id=state.projects[0]?.id||'';resetSelection();}else state.id=wanted;
    $('#project-select').innerHTML=state.projects.length ? state.projects.map(p=>`<option value="${esc(p.id)}" ${p.id===state.id?'selected':''}>${esc(p.title||p.id)}</option>`).join('') : '<option>Aucun projet</option>';
    if(!state.id){state.project=null;state.fingerprint='';$('#project-name').textContent='—';$('#content').innerHTML=empty('L’atelier attend son premier film','Ajoute un dossier de projet dans le répertoire projects. Il apparaîtra ici automatiquement.');}
    else{
      const data=await getJSON(`/api/projects/${encodeURIComponent(state.id)}`); const fingerprint=JSON.stringify(data);
      state.project=data;$('#project-name').textContent=data.title||data.id;
      if(force || fingerprint!==state.fingerprint){
        state.fingerprint=fingerprint;
        const focus=document.activeElement?.id;
        const cursor=focus==='media-search' ? document.activeElement.selectionStart : null;
        render();
        if(focus==='media-search' && $('#media-search')){$('#media-search').focus();try{$('#media-search').setSelectionRange(cursor,cursor);}catch{}}
        if(state.modal){
          const item=modalItem(state.modal.kind,state.modal.id);
          if(!item)closeModal();
          else if(JSON.stringify(item)!==state.modal.snapshot)showModal(state.modal.kind,state.modal.id,true);
        }
      }
      const url=new URL(location.href);url.searchParams.set('project',state.id);history.replaceState(null,'',url);
    }
    $('#connection').textContent='Fichiers synchronisés';$('#sync-time').textContent=`À jour à ${new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}`;
  }catch(e){$('#connection').textContent='Connexion interrompue';$('#sync-time').textContent='Nouvelle tentative automatique';if(!state.project)$('#content').innerHTML=empty('L’atelier est momentanément indisponible',`${e.message} Vérifie que le serveur local est lancé.`);}
  finally{state.busy=false;}
}
function setView(view){state.view=view;render();window.scrollTo({top:0,behavior:'instant'});}
function render(){
  for(const b of document.querySelectorAll('[data-view].nav-item')){b.classList.toggle('active',b.dataset.view===state.view);if(b.dataset.view===state.view)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');}
  if(!state.project)return;
  const views={overview:overviewView,production:productionView,storyboard:storyboardView,scenes:scenesView,media:mediaView,relations:relationsView,sources:sourcesView};
  $('#content').innerHTML=(views[state.view]||overviewView)();
  if(state.view==='relations')requestAnimationFrame(drawConnections);
}
function stageStrip(){return `<div class="pipeline">${array(state.project.stages).map((s,i)=>`<div class="stage ${esc(s.status)}"><div class="number">${String(i+1).padStart(2,'0')} /</div><div class="stage-name">${esc(s.label)}</div><div class="stage-status">${esc(labels[s.status]||s.status)}${s.count?` · ${esc(s.count)}`:''}</div></div>`).join('')}</div>`;}
function shotCard(shot){const image=shotImages(shot)[0];const media=shotMedia(shot).filter(m=>m.role!=='reference');return `<button class="shot-card" data-action="shot" data-id="${esc(shot.id)}"><div class="visual">${image?img(image,titleOf(shot)):`<div class="visual-placeholder">${esc(short(displayId(shot.id),18))}</div>`}<span class="tag">${esc(shot.scene_id||'SCÈNE NON RELIÉE')}</span>${shot.duration_seconds?`<span class="duration">${esc(shot.duration_seconds)} s</span>`:''}</div><div class="card-body"><div class="card-label">${esc(shot.id)}</div><h3 class="card-title">${esc(titleOf(shot))}</h3><p class="card-description">${esc(short(shot.description || 'Description non renseignée',160))}</p><div class="card-bottom"><span>${media.length?`${media.length} média${media.length>1?'s':''}`:'Rendu à préparer'}</span><span class="dim">EXPLORER ↗</span></div></div></button>`;}
function entityPill(entity){const reference=imagesFor(entity.media_ids)[0];return `<button class="entity-pill" data-action="entity" data-id="${esc(entity.id)}">${reference?img(reference,titleOf(entity)):''}<span>${esc(titleOf(entity))} <small>${esc(labels[entity.kind]||entity.kind)}</small></span></button>`;}
function overviewView(){
  const p=state.project;const cover=p.cover || array(p.media).find(m=>m.kind==='image'&&m.role==='shot'&&!m.archived) || array(p.media).find(m=>m.kind==='image'&&!m.archived);
  const progress=Math.max(0,Math.min(100,Number(p.progress)||0));const scenes=array(p.scenes);const shots=array(p.shots);const media=array(p.media);const warnings=array(p.warnings);const next=nextStage();
  const sheetStage=array(p.stages).find(s=>s.id==='reference_sheets');const references={length:Number(sheetStage?.count)||0};const approvedReferences={length:Number(sheetStage?.documented_approvals)||0};
  return `<section class="hero">${cover?img(cover,'','hero-img'):''}<span class="hero-index">CARNET DE PRODUCTION / ${esc(p.id.toUpperCase())}</span><div class="hero-text"><div class="eyebrow">CHAQUE PLAN RAPPROCHE LE FILM.</div><h1>${esc(p.title||p.id)}</h1><p>${esc(short(p.description||'Un projet, ses idées, ses plans et ses images. Tout le parcours du film dans un même atelier.',240))}</p><div class="hero-meta"><span>${esc(p.genre||'PROJET LOCAL')}</span>${p.duration_seconds?`<span>${esc(Math.round(p.duration_seconds/60*10)/10)} MIN</span>`:''}${p.aspect_ratio?`<span>${esc(p.aspect_ratio)}</span>`:''}<span>${esc(formatDate(p.updated_at))}</span><span>LECTURE SEULE</span></div></div><span class="hero-mark">A·</span></section>
  <section class="stats" aria-label="Indicateurs du projet"><div class="stat"><div class="stat-label">PROCHAINE ÉTAPE</div><div class="stat-value stat-text">${esc(next?next.label:'Revue finale')}</div><div class="stat-note">${array(p.stages).filter(s=>s.status==='present').length}/${array(p.stages).length} étapes avec fichiers</div><div class="progress-track"><i style="width:${progress}%"></i></div></div><div class="stat"><div class="stat-label">PLANCHES DE RÉFÉRENCE</div><div class="stat-value">${pad2(references.length)}</div><div class="stat-note">${approvedReferences.length} approuvée${approvedReferences.length>1?'s':''} au registre</div></div><div class="stat"><div class="stat-label">PLANS</div><div class="stat-value">${pad2(shots.length)}</div><div class="stat-note">${shots.length?`${shots.filter(s=>shotImages(s).length).length} avec keyframe · ${scenes.length} scène${scenes.length>1?'s':''}`:'Découpage à venir'}</div></div><div class="stat"><div class="stat-label">ENGAGÉ</div><div class="stat-value stat-text">${p.budget?.ledger?.available?esc(money(p.budget.ledger.committed_usd)):'—'}</div><div class="stat-note">${typeof p.budget?.decision?.max_spend_usd==='number'?`sur un plafond de ${esc(money(p.budget.decision.max_spend_usd))}`:'Plafond non renseigné'}</div></div></section>
  <div class="section-heading"><div><h2>Le parcours du film</h2><small>OÙ EN EST LA MÉTHODE</small></div><button class="text-button" data-view="production">Suivi de production ↗</button></div>${tracker(true)}
  ${shots.length?`<div class="section-heading"><div><h2>Sur la table de montage</h2><small>UN APERÇU DES PLANS DU PROJET</small></div><button class="text-button" data-view="scenes">Tous les plans ↗</button></div><div class="grid">${shots.slice(0,4).map(shotCard).join('')}</div>`:`<div class="section-heading"><div><h2>La bible visuelle</h2><small>LE DÉCOUPAGE N’EXISTE PAS ENCORE — VOICI LES RÉFÉRENCES DU FILM</small></div><button class="text-button" data-view="production">Suivi complet ↗</button></div>${bibleSection()}`}
  <div class="overview-bottom"><section class="panel"><h3>Le monde du film</h3>${array(p.entities).length?`<div class="entity-list">${array(p.entities).slice(0,10).map(entityPill).join('')}</div>`:'<p class="intro">Personnages, lieux et accessoires apparaîtront à partir de leurs fiches.</p>'}</section><section class="panel"><h3>À garder en vue</h3>${warnings.length?`<p class="intro">${warnings.length} point${warnings.length>1?'s':''} à vérifier dans les fichiers.</p><div class="alert">${esc(short(warnings[0],220))}</div>`:'<p class="intro">Aucune alerte de lecture signalée. Cela ne remplace pas un audit de continuité.</p>'}<button class="text-button" data-view="sources">Documents, budget & alertes ↗</button></section></div>`;
}
function scenesView(){const p=state.project;const scenes=array(p.scenes);const shots=array(p.shots);let html=heading('DÉCOUPAGE DU FILM','D’une scène à l’autre.','Le storyboard du projet, organisé à partir des liens de scène et de plan présents dans les documents.');
  if(!scenes.length&&!shots.length)return html+empty('Le storyboard attend ses premières scènes','Ajoute le scénario et les plans au projet pour explorer leur découpage.','▤');
  html+=scenes.map((s,i)=>{const related=shots.filter(x=>x.scene_id===s.id||array(s.shot_ids).includes(x.id));return `<section class="scene-block"><div class="scene-head"><span class="scene-number">${String(i+1).padStart(2,'0')}</span><div><div class="card-label">${esc(s.id)}</div><h2>${esc(titleOf(s))}</h2><p>${esc(short(s.description,220))}${s.location_id?` · ${esc(s.location_id)}`:''}</p></div><span class="scene-count">${related.length} PLAN${related.length>1?'S':''}</span></div>${related.length?`<div class="grid">${related.map(shotCard).join('')}</div>`:empty('Aucun plan relié','Cette scène n’a pas encore de plan associé.')}</section>`;}).join('');
  const orphan=shots.filter(s=>!scenes.some(c=>s.scene_id===c.id||array(c.shot_ids).includes(s.id)));if(orphan.length)html+=`<div class="section-heading"><h2>Plans sans scène documentée</h2></div><div class="grid">${orphan.map(shotCard).join('')}</div>`;return html;
}
function mediaCard(m){const name=mediaLabel(m);return `<button class="media-card" data-action="media" data-id="${esc(m.id)}"><div class="visual">${m.kind==='image'?img(m,name):`<div class="visual-placeholder ${esc(m.kind)}">${m.kind==='video'?'▷':'▂ ▅ ▃ ▇ ▄'}</div>`}<span class="tag">${esc(m.derived_from?`Vue${m.view?` · ${m.view}`:''}`:labels[m.kind]||m.kind)}</span>${array(m.reference_approvals).length?'<span class="approved-tag" title="Approbation documentée dans un registre">✓</span>':''}</div><div class="card-body"><div class="card-label">${esc(labels[m.role]||m.role)}</div><h3 class="card-title">${esc(short(name,65))}</h3><div class="card-bottom"><span>${array(m.shot_ids).length?esc(m.shot_ids.join(', ')):array(m.entity_ids).length?esc(m.entity_ids.join(', ')):'Association non documentée'}</span><span class="dim">↗</span></div></div></button>`;}
function filteredMedia(){const shot=array(state.project.shots).find(s=>s.id===state.shotFilter);const entity=array(state.project.entities).find(e=>e.id===state.entityFilter);return array(state.project.media).filter(m=>(state.mediaType==='all'||m.kind===state.mediaType)&&(state.mediaRole==='all'||m.role===state.mediaRole)&&(!state.shotFilter||touchesShot(m,shot))&&(!state.entityFilter||belongsToEntity(m,entity))&&(`${m.path} ${array(m.shot_ids).join(' ')} ${array(m.entity_ids).join(' ')} ${array(m.usage_records).flatMap(r=>array(r.shot_ids)).join(' ')}`).toLowerCase().includes(state.search.toLowerCase()));}
function mediaView(){return heading('LES IMAGES DU FILM','La matière visuelle.','Références, essais et rendus : chaque version reste visible. Les médias sans lien documenté sont conservés à part.')+`<div class="toolbar"><input id="media-search" class="search" type="search" aria-label="Rechercher un média" placeholder="Rechercher un fichier, un plan, un personnage…" value="${esc(state.search)}"><select id="media-type" aria-label="Type de média">${[['all','Tous les médias'],['image','Images'],['video','Vidéos'],['audio','Audio']].map(([v,l])=>`<option value="${v}" ${state.mediaType===v?'selected':''}>${l}</option>`).join('')}</select><select id="media-role" aria-label="Rôle du média">${[['all','Tous les usages'],['shot','Rendus de plans'],['reference','Références'],['unlinked','Non reliés']].map(([v,l])=>`<option value="${v}" ${state.mediaRole===v?'selected':''}>${l}</option>`).join('')}</select>${state.shotFilter||state.entityFilter?`<span class="filter-chip">${esc(state.shotFilter||state.entityFilter)}<button data-action="clear-filter" aria-label="Effacer le filtre">×</button></span>`:''}</div><div id="media-results">${mediaResults()}</div>`;}
function mediaResults(){const media=filteredMedia();return `<div class="gallery-count">${media.length} MÉDIA${media.length>1?'S':''} · FICHIERS EXISTANTS SUR DISQUE</div>`+(media.length?`<div class="grid">${media.map(mediaCard).join('')}</div>`:empty('Pas encore d’image dans cette sélection','Les fichiers trouvés dans le projet apparaissent ici, même lorsque leur association est inconnue.','▧'));}

function relationsView(){const p=state.project;const shots=array(p.shots);const s=shots.find(x=>x.id===state.relationShot)||shots[0];if(s)state.relationShot=s.id;
  let h=heading('LA CARTOGRAPHIE DU PROJET','Tout est lié. Ou reste à l’être.','Choisis un plan pour comprendre son origine, ses références et ses rendus. Seules les relations présentes dans les fichiers sont représentées.');
  if(!s)return h+empty('Aucune connexion à tracer','Le projet doit contenir des plans identifiés pour afficher leurs relations.','⌘');
  const scene=array(p.scenes).find(c=>c.id===s.scene_id||array(c.shot_ids).includes(s.id));const entities=shotEntities(s);const references=shotReferences(s);const renders=shotMedia(s).filter(m=>m.role!=='reference');const prompts=array(s.prompts);
  const node=(key,body,action,id,active=false)=>`<${action?'button':'div'} class="connection-node ${active?'active-node':''}" data-node="${esc(key)}" ${action?`data-action="${esc(action)}" data-id="${esc(id)}"`:''}>${body}</${action?'button':'div'}>`;
  const cols=[scene?node('scene',`<h3>${esc(titleOf(scene))}</h3><p>${esc(scene.id)}</p>`):'<div class="connection-missing">Scène non documentée</div>',node('shot',`<h3>${esc(titleOf(s))}</h3><p>${esc(s.id)}</p>${s.duration_seconds?badge(s.duration_seconds+' s'):''}`,'shot',s.id,true),references.slice(0,8).map((m,i)=>node('ref-'+i,`${m.kind==='image'?img(m,m.path):''}<h3>${esc(short(mediaLabel(m),40))}</h3><p>${inputUsesFor(m,s).length?'Entrée du plan':esc(array(m.entity_ids).join(', '))}</p>${relationBadge(inputRelation(m,s))}`,'media',m.id)).join('')||'<div class="connection-missing">Aucune référence média reliée</div>',prompts.slice(0,8).map((a,i)=>{const artifact=typeof a==='string'?array(p.artifacts).find(x=>x.path===a):a;return node('prompt-'+i,`<h3>${esc(short(artifact?.path||a?.prompt_id||a?.id||'Prompt',55))}</h3><p>${esc(artifact?.kind||'prompt')}</p>`,'artifact',artifact?.path||text(a));}).join('')||'<div class="connection-missing">Aucun prompt relié</div>',renders.slice(0,10).map((m,i)=>node('render-'+i,`${m.kind==='image'?img(m,m.path):''}<h3>${esc(short(mediaLabel(m),40))}</h3><p>${esc(labels[m.kind])}</p>${relationBadge(m)}`,'media',m.id)).join('')||'<div class="connection-missing">Aucun rendu relié</div>'];
  h+=`<div class="toolbar"><select id="relation-shot" aria-label="Plan à explorer">${shots.map(x=>`<option value="${esc(x.id)}" ${s.id===x.id?'selected':''}>${esc(x.id)} · ${esc(short(titleOf(x),55))}</option>`).join('')}</select><div class="legend"><span><i></i>Documenté</span><span><i class="dashed"></i>Nom de fichier / origine inconnue</span></div></div><div class="connection-scroll"><div class="connection-board"><svg aria-hidden="true"></svg>${['01 / SCÈNE','02 / PLAN','03 / RÉFÉRENCES','04 / PROMPTS','05 / RENDUS'].map((l,i)=>`<div class="connection-col"><div class="connection-label">${l}</div>${cols[i]}</div>`).join('')}</div></div><p class="relation-note">Les traits montrent des associations, pas une preuve de filiation entre un prompt et une image. ${renders.length>10?'Seuls les 10 premiers rendus sont représentés ; toutes les versions restent dans la médiathèque.':''}</p>${entities.length?`<div class="section-heading"><h2>Les éléments de ce plan</h2></div><div class="entity-list">${entities.map(entityPill).join('')}</div>`:''}<div class="section-heading"><h2>Toutes les versions du plan</h2><button class="text-button" data-action="filter-shot" data-id="${esc(s.id)}">Explorer les médias ↗</button></div>`;return h;
}
function drawConnections(){const board=$('.connection-board');if(!board)return;const svg=$('svg',board);const r=board.getBoundingClientRect();const s=array(state.project.shots).find(x=>x.id===state.relationShot);if(!s)return;
  const edges=[];if($('[data-node="scene"]',board))edges.push(['scene','shot',false]);shotReferences(s).slice(0,8).forEach((m,i)=>edges.push(['shot','ref-'+i,relationKind(inputRelation(m,s))!=='explicit']));for(const node of board.querySelectorAll('[data-node^="prompt-"]'))edges.push(['shot',node.dataset.node,false]);const media=shotMedia(s).filter(m=>m.role!=='reference').slice(0,10);media.forEach((m,i)=>edges.push(['shot','render-'+i,relationKind(m)!=='explicit']));
  svg.setAttribute('viewBox',`0 0 ${r.width} ${r.height}`);svg.innerHTML=edges.map(([a,b,dashed])=>{const from=board.querySelector(`[data-node="${a}"]`)?.getBoundingClientRect();const to=board.querySelector(`[data-node="${b}"]`)?.getBoundingClientRect();if(!from||!to)return '';const x1=from.right-r.left,y1=from.top-r.top+from.height/2,x2=to.left-r.left,y2=to.top-r.top+to.height/2;const mid=(x1+x2)/2;return `<path d="M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}" fill="none" stroke="${dashed?'#8a8d7b':'#b68f62'}" stroke-width="1" opacity=".48" ${dashed?'stroke-dasharray="4 5"':''}/>`;}).join('');
}
function sourcesView(){const p=state.project;return heading('LE CARNET DE PRODUCTION','Les preuves derrière les images.','Les documents sont lus depuis le disque et vérifiés lorsqu’un schéma est disponible. Rien n’est modifié depuis cet atelier.')+`<div class="overview-bottom"><section class="panel"><h3>Suivi budgétaire</h3>${p.budget?`<p class="intro">La revue du budget concerne la planification, jamais une autorisation automatique de dépense.</p><pre class="source-code">${esc(JSON.stringify(p.budget,null,2))}</pre>`:'<p class="intro">Aucun suivi budgétaire disponible dans ce projet. Les coûts inconnus ne sont pas considérés comme nuls.</p>'}</section><section class="panel"><h3>Points à vérifier</h3>${array(p.warnings).length?`<ul class="warning-list">${array(p.warnings).slice(0,40).map(w=>`<li>${esc(w)}</li>`).join('')}</ul>${p.warnings.length>40?'<p class="intro">Les 40 premières alertes sont affichées.</p>':''}`:'<p class="intro">Aucune alerte de lecture. La présence des fichiers ne garantit pas leur validation artistique ou technique.</p>'}</section></div><div class="section-heading"><h2>Documents du projet</h2><small>${array(p.artifacts).length} DOCUMENTS</small></div>${array(p.artifacts).length?`<div class="document-list">${array(p.artifacts).map(a=>`<button class="document-row" data-action="artifact" data-id="${esc(a.path)}"><span><b>${esc(a.path)}</b><small>${esc(a.kind||'Document')}</small></span>${badge(a.valid===true?'Schéma valide':a.valid===false?'À vérifier':'Non vérifié',a.valid===true?'good':a.valid===false?'warn':'')}</button>`).join('')}</div>`:empty('Aucun document lisible','Les fichiers YAML du projet apparaîtront ici.')}`;}

function modalHeader(title){return `<div class="inspector-head"><h2 id="inspector-title">${esc(title)}</h2><button class="close-button" data-action="close" aria-label="Fermer">×</button></div>`;}
function showModal(kind,id,preservePlayer=false){
  const p=state.project;if(!p||!modalItem(kind,id)){closeModal();return;}let body='',title='';
  const existingPlayer=preservePlayer ? $('#inspector').querySelector('video, audio') : null;
  const playback=existingPlayer ? {time:existingPlayer.currentTime,volume:existingPlayer.volume,muted:existingPlayer.muted,rate:existingPlayer.playbackRate,paused:existingPlayer.paused,focused:document.activeElement===existingPlayer} : null;
  if(kind==='media'){
    const m=mediaById(id);if(!m)return;title=mediaLabel(m);const url=mediaUrl(m);
    body=(m.kind==='image'?`<img class="preview-image" src="${esc(url)}" alt="${esc(title)}">`:m.kind==='video'?`<video class="preview-video" controls preload="metadata" src="${esc(url)}"></video>`:`<audio class="preview-audio" controls preload="metadata" src="${esc(url)}"></audio>`)+`<div class="inspector-meta">${badge(labels[m.kind])}${badge(labels[m.role])}${relationBadge(m)}${reviewBadges(m)}</div><p class="source-path">${esc(m.path)}<br>${esc(formatDate(m.modified_at))}</p><div class="entity-list">${array(m.shot_ids).map(s=>`<button class="entity-pill" data-action="shot" data-id="${esc(s)}">Plan source · ${esc(s)} ↗</button>`).join('')}${array(m.entity_ids).map(e=>array(p.entities).find(x=>x.id===e)).filter(Boolean).map(entityPill).join('')}</div>${array(m.prompt_ids).length?`<p class="source-path">Prompts sources : ${esc(m.prompt_ids.join(', '))}</p>`:''}${!array(m.shot_ids).length&&!array(m.entity_ids).length&&!array(m.usage_records).length?'<div class="alert">Ce média est présent, mais aucun lien vers un plan ou une entité n’est documenté.</div>':''}<a class="button subtle" href="${esc(url)}" target="_blank" rel="noopener">Ouvrir le fichier ↗</a>`;
    if(array(m.reference_approvals).length)body+=`<h3>Approbation documentée</h3>${m.reference_approvals.map(approvalBlock).join('')}<p class="relation-note">L’approbation porte sur ce fichier précis ; son périmètre exact (angles, tenue, usage) est décrit dans le registre et les notes.</p>`;
    else if(m.role==='reference'&&!m.derived_from)body+=`<p class="relation-note">Aucune approbation au registre pour ce fichier : c’est une candidate ou une source.</p>`;
    if(m.derived_from){const parent=mediaById(m.derived_from);body+=`<h3>Vue dérivée</h3><p class="intro">Recadrage${m.view?` « ${esc(m.view)} »`:''} d’une planche. Il n’hérite d’aucune approbation propre.</p>${parent?`<button class="entity-pill" data-action="media" data-id="${esc(parent.id)}">${img(parent,'')}<span>Planche source · ${esc(mediaLabel(parent))}</span></button>`:''}`;}
    if(array(m.notes).length)body+=`<h3>Notes de revue</h3><div class="document-list">${m.notes.map(n=>`<button class="document-row" data-action="artifact" data-id="${esc(n)}"><b>${esc(n)}</b><span>Lire ↗</span></button>`).join('')}</div>`;
    if(array(m.usage_records).length)body+=`<h3>Utilisations comme entrée</h3><p class="intro">Une utilisation ne change pas l’identité de l’asset et ne lui transmet pas l’approbation du résultat.</p>${array(m.usage_records).map(r=>`<div class="panel"><button class="text-button source-path" data-action="artifact" data-id="${esc(r.path)}">${esc(r.path)} ↗</button><div class="entity-list">${array(r.shot_ids).map(id=>`<button class="entity-pill" data-action="shot" data-id="${esc(id)}">Plan destinataire · ${esc(id)}</button>`).join('')}</div></div>`).join('')}`;
    if(array(m.review_records).length)body+=`<details><summary class="relation-note">Historique des statuts et validations (${m.review_records.length})</summary><pre class="source-code">${esc(JSON.stringify(m.review_records,null,2))}</pre></details>`;
  }else if(kind==='shot'){
    const s=array(p.shots).find(x=>x.id===id);if(!s)return;title=`${shotLabel(s)} — ${titleOf(s)}`;const media=[...new Map([...shotMedia(s),...shotReferences(s)].map(m=>[m.id,m])).values()];const entities=shotEntities(s);const pr=shotProgress(s);
    body=`<div class="inspector-meta">${badge(s.id)}${badge(s.scene_id||'Scène non reliée')}${s.duration_seconds?badge(s.duration_seconds+' s'):''}${typeof s.start_seconds==='number'?badge(`à ${timecode(s.start_seconds)}`):''}</div><div class="shot-progress">${[['image_prompt','Prompt image'],['keyframe','Keyframe'],['video_prompt','Prompt vidéo'],['video','Vidéo'],['audio','Son']].map(([k,l])=>`<span>${cell(pr[k])}<small>${esc(l)}</small></span>`).join('')}</div><p class="detail-description">${esc(text(s.description)||'Description non renseignée.')}</p><div class="entity-list">${entities.map(entityPill).join('')}</div><div class="section-heading"><h3>Références & versions</h3><button class="text-button" data-action="relations" data-id="${esc(s.id)}">Voir les connexions ↗</button></div>${media.length?`<div class="grid">${media.map(mediaCard).join('')}</div>`:empty('Pas encore de média relié','Les rendus et références associés à ce plan apparaîtront ici.')}${array(p.panels).filter(x=>x.shot_id===s.id).length?`<h3>Storyboard</h3><div class="storyboard-grid">${array(p.panels).filter(x=>x.shot_id===s.id).map(panelCard).join('')}</div>`:''}<h3>Prompts associés</h3>${array(s.prompts).length?array(s.prompts).map(a=>{const path=typeof a==='string'?a:a.path;return `<button class="document-row" data-action="artifact" data-id="${esc(path)}"><b>${esc(path)}</b><span>↗</span></button>`;}).join(''):'<p class="intro">Aucun prompt documenté pour ce plan.</p>'}`;
  }else if(kind==='entity'){
    const e=array(p.entities).find(x=>x.id===id);if(!e)return;title=titleOf(e);const media=array(p.media).filter(m=>array(e.media_ids).includes(m.id)||array(m.entity_ids).includes(e.id));const shots=array(p.shots).filter(s=>array(s.characters).includes(e.id)||array(s.props).includes(e.id)||s.location_id===e.id);
    const groups=new Map();for(const m of media.filter(m=>!m.derived_from)){const folder=text(m.path).split('/').slice(0,-1).join('/')||'.';if(!groups.has(folder))groups.set(folder,[]);groups.get(folder).push(m);}
    for(const m of media.filter(m=>m.derived_from)){const parent=mediaById(m.derived_from);const folder=parent?text(parent.path).split('/').slice(0,-1).join('/')||'.':'Vues dérivées';if(!groups.has(folder))groups.set(folder,[]);groups.get(folder).push(m);}
    const ordered=[...groups.entries()].sort((a,b)=>Math.max(...b[1].map(m=>m.modified_at||0))-Math.max(...a[1].map(m=>m.modified_at||0)));
    const notes=[...new Set(media.flatMap(m=>array(m.notes)))];
    body=`<div class="inspector-meta">${badge(labels[e.kind]||e.kind)}${badge(e.id)}${e.source?badge(`Déclaré dans ${e.source}`):''}</div><p class="detail-description">${esc(text(e.description)||'Aucune description dans les fichiers du projet. Les notes de revue détaillent l’apparence retenue.')}</p>
    <h3>Planches & essais</h3>${ordered.length?ordered.map(([folder,items])=>{const approved=items.filter(m=>array(m.reference_approvals).length);return `<section class="attempt"><div class="attempt-head"><b>${esc(folder.split('/').slice(-2).join(' / '))}</b>${approved.length?badge(`${approved.length} approuvée${approved.length>1?'s':''} au registre`,'good'):badge('Sans approbation au registre')}</div><div class="grid">${items.map(mediaCard).join('')}</div>${approved.flatMap(m=>m.reference_approvals.filter(r=>r.entity_id===e.id)).map(approvalBlock).join('')}</section>`;}).join(''):empty('Aucune référence média documentée','L’entité existe, mais aucune illustration n’y est encore reliée.')}
    ${notes.length?`<h3>Notes de revue</h3><div class="document-list">${notes.map(n=>`<button class="document-row" data-action="artifact" data-id="${esc(n)}"><b>${esc(n)}</b><span>Lire ↗</span></button>`).join('')}</div>`:''}
    <h3>Présence dans les plans</h3>${shots.length?`<div class="grid">${shots.map(shotCard).join('')}</div>`:'<p class="intro">Aucun plan relié pour l’instant.</p>'}`;
  }else if(kind==='panel'){
    const panel=array(p.panels).find(x=>x.id===id);if(!panel)return;const shot=array(p.shots).find(s=>s.id===panel.shot_id);const scene=array(p.scenes).find(c=>c.id===panel.scene_id);
    title=`Case ${pad2(panel.order||1)}${panel.title?` — ${panel.title}`:''}`;const frames=array(panel.media_ids).map(mediaById).filter(Boolean);
    const entities=array(p.entities).filter(e=>array(panel.characters).includes(e.id)||panel.location_id===e.id);
    const fields=[['Composition',panel.composition],['Caméra',panel.camera],['Action',panel.action],['Lumière',panel.lighting],['Émotion',panel.emotion],['Son',panel.sound],['Continuité',panel.continuity]].filter(([,v])=>v);
    body=`${frames[0]?.kind==='image'?`<img class="preview-image" src="${esc(mediaUrl(frames[0]))}" alt="">`:`<div class="panel-sketch large"><span>${esc(panel.composition||panel.action||'Cadre non dessiné')}</span></div>`}
    <div class="inspector-meta">${badge(panel.id)}${scene?badge(scene.number!=null?`Scène ${scene.number}`:scene.id):badge(panel.scene_id||'Scène non reliée')}${panel.duration_seconds?badge(`${panel.duration_seconds} s`):''}${panel.needs_motion===true?badge('Mouvement prévu'):panel.needs_motion===false?badge('Plan fixe'):''}${frames.length?badge('Dessin de storyboard'):badge('Pas encore de dessin')}</div>
    ${shot?`<button class="entity-pill" data-action="shot" data-id="${esc(shot.id)}">Plan ${esc(shotLabel(shot))} · ${esc(short(titleOf(shot),60))} ↗</button>`:panel.shot_id?`<p class="relation-note">Plan prévu : ${esc(panel.shot_id)} (pas encore dans la liste des plans).</p>`:''}
    <dl class="panel-fields">${fields.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl>
    ${entities.length?`<div class="entity-list">${entities.map(entityPill).join('')}</div>`:''}
    ${frames.length>1?`<h3>Autres dessins</h3><div class="grid">${frames.slice(1).map(mediaCard).join('')}</div>`:''}
    <button class="document-row" data-action="artifact" data-id="${esc(panel.source)}"><b>${esc(panel.source)}</b><span>Source ↗</span></button>
    <p class="relation-note">Un dessin de storyboard sert à valider le cadrage et le rythme ; ce n’est ni une keyframe ni un rendu de plan.</p>`;
  }else if(kind==='artifact'){
    const a=array(p.artifacts).find(x=>x.path===id);if(!a)return;title=a.path;
    if(a.kind==='note'){body=`<div class="inspector-meta">${badge('Note')}${badge('Texte affiché tel quel')}</div>${array(a.errors).length?`<div class="alert error">${array(a.errors).map(esc).join('<br>')}</div>`:''}<pre class="note-text">${esc(text(a.data))}</pre><p class="intro">Lecture seule · Une note décrit une décision ; elle n’est pas interprétée automatiquement comme une approbation.</p>`;}
    else body=`<div class="inspector-meta">${badge(a.kind||'Document')}${badge(a.valid===true?'Schéma valide':a.valid===false?'À vérifier':'Sans validation disponible',a.valid===true?'good':a.valid===false?'warn':'')}</div>${array(a.errors).length?`<div class="alert error">${array(a.errors).map(esc).join('<br>')}</div>`:''}<pre class="source-code">${esc(JSON.stringify(a.data,null,2))}</pre><p class="intro">Lecture seule · La validation de schéma ne constitue pas une approbation de génération.</p>`;
  }else return;
  state.modal={kind,id,snapshot:JSON.stringify(modalItem(kind,id))};$('#inspector-content').innerHTML=modalHeader(title)+`<div class="inspector-body">${body}</div>`;if(!$('#inspector').open)$('#inspector').showModal();
  if(playback){const player=$('#inspector').querySelector('video, audio');if(player){player.volume=playback.volume;player.muted=playback.muted;player.playbackRate=playback.rate;const restore=()=>{player.currentTime=playback.time;if(!playback.paused)player.play().catch(()=>{});};if(player.readyState>=1)restore();else player.addEventListener('loadedmetadata',restore,{once:true});if(playback.focused)player.focus();}}
}
function closeModal(){$('#inspector').close();state.modal=null;$('#inspector-content').innerHTML='';}
function approvalBlock(r){return `<blockquote class="approval"><div>${badge(`Registre · ${r.approved_at||'date inconnue'}`,'good')}${r.sheet_type?badge(r.sheet_type):''}${r.order!=null?badge(`Ordre ${r.order}`):''}</div>${r.consent_verbatim?`<p>« ${esc(r.consent_verbatim)} »</p>`:'<p>Réponse exacte non renseignée.</p>'}<small>${esc(r.path)}</small></blockquote>`;}
document.addEventListener('keydown',e=>{const row=e.target.closest?.('tr[data-action]');if(row&&(e.key==='Enter'||e.key===' ')){e.preventDefault();showModal(row.dataset.action,row.dataset.id);}});
document.addEventListener('click',e=>{
  const b=e.target.closest('button, tr[data-action]');if(!b)return;
  if(b.dataset.view){setView(b.dataset.view);return;}
  const action=b.dataset.action,id=b.dataset.id;
  if(['media','shot','entity','artifact','panel'].includes(action))showModal(action,id);
  else if(action==='close')closeModal();
  else if(action==='relations'){closeModal();state.relationShot=id;setView('relations');}
  else if(action==='filter-shot'){state.shotFilter=id;state.entityFilter='';state.search='';state.mediaRole='all';state.mediaType='all';setView('media');}
  else if(action==='clear-filter'){state.shotFilter='';state.entityFilter='';render();}
});
document.addEventListener('input',e=>{if(e.target.id==='media-search'){state.search=e.target.value;$('#media-results').innerHTML=mediaResults();}});
document.addEventListener('change',e=>{
  if(e.target.id==='project-select'){if(state.busy){e.target.value=state.id;return;}closeModal();state.id=e.target.value;state.fingerprint='';state.shotFilter='';state.entityFilter='';state.relationShot='';state.search='';refresh(true);}
  if(e.target.id==='media-type'){state.mediaType=e.target.value;$('#media-results').innerHTML=mediaResults();}
  if(e.target.id==='media-role'){state.mediaRole=e.target.value;$('#media-results').innerHTML=mediaResults();}
  if(e.target.id==='relation-shot'){state.relationShot=e.target.value;render();}
});
$('#refresh').addEventListener('click',()=>refresh(true));
$('#inspector').addEventListener('cancel',e=>{e.preventDefault();closeModal();});
$('#inspector').addEventListener('click',e=>{if(e.target===$('#inspector')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeModal();}});
window.addEventListener('resize',()=>{if(state.view==='relations')drawConnections();});
refresh();setInterval(()=>{if(!document.hidden)refresh();},5000);

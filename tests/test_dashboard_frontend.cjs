// Dependency-free rendering smoke tests: node --test tests/test_dashboard_frontend.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function app() {
  const elements = new Map();
  const document = {
    hidden: false,
    querySelector(selector) {
      if (!elements.has(selector)) elements.set(selector, {
        innerHTML: '', textContent: '', open: false,
        addEventListener() {}, showModal() { this.open = true; },
        close() { this.open = false; },
        querySelector() { return null; },
      });
      return elements.get(selector);
    },
    querySelectorAll() { return []; },
    addEventListener() {},
  };
  const ctx = vm.createContext({document, window: {addEventListener() {}, scrollTo() {}},
    location: {href: 'http://127.0.0.1:8765/', search: ''}, history: {replaceState() {}},
    URL, URLSearchParams, setInterval() {}, requestAnimationFrame() {},
    fetch: async () => ({ok: true, json: async () => ({projects: []})}), console});
  const source = fs.readFileSync(path.join(__dirname, '../src/dashboard/static/app.js'), 'utf8')
    .replace('refresh();setInterval(()=>{if(!document.hidden)refresh();},5000);', '');
  vm.runInContext(source, ctx);
  return {ctx, evaluate: script => vm.runInContext(script, ctx), elements};
}

test('all views render an incomplete project without inventing content', () => {
  const {evaluate} = app();
  evaluate(`state.project={id:'empty-film',title:'Nouveau film',scenes:[],shots:[],media:[],entities:[],artifacts:[],stages:[],warnings:[]};`);
  for (const view of ['overviewView', 'scenesView', 'mediaView', 'relationsView', 'sourcesView']) {
    const html = evaluate(`${view}()`);
    assert.ok(html.length > 100, view);
    assert.ok(!html.includes('undefined'), view);
    assert.ok(!html.includes('NaN'), view);
  }
});

test('project text and attribute values are escaped; arbitrary media URLs are rejected', () => {
  const {evaluate} = app();
  evaluate(`state.project={id:'test',title:'<script>alert(1)</script>',description:'<img onerror=evil()>',shots:[],media:[],scenes:[],entities:[],stages:[],warnings:[]};`);
  const html = evaluate('overviewView()');
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;'));
  assert.equal(evaluate(`mediaUrl({url:'javascript:alert(1)'})`), '');
  assert.equal(evaluate(`mediaUrl({url:'https://external.test/picture.png'})`), '');
  assert.equal(evaluate(`esc('" onerror="x')`), '&quot; onerror=&quot;x');
});

test('references remain distinct from shot render thumbnails and media filters work', () => {
  const {evaluate} = app();
  evaluate(`state.project={id:'fixture',title:'Fixture',scenes:[{id:'scene_A',title:'Scène A',shot_ids:['shot_A']}],shots:[{id:'shot_A',scene_id:'scene_A',title:'Plan A',media_ids:['reference.png','render.png'],characters:['char_A'],prompts:[]}],entities:[{id:'char_A',kind:'character',name:'Personnage A',media_ids:['reference.png']}],media:[{id:'reference.png',path:'reference.png',url:'/media/fixture/reference.png',kind:'image',role:'reference',shot_ids:['shot_A'],entity_ids:['char_A']},{id:'render.png',path:'render.png',url:'/media/fixture/render.png',kind:'image',role:'shot',shot_ids:['shot_A'],entity_ids:[],relation:'filename'}],artifacts:[],stages:[],warnings:[]};`);
  assert.equal(evaluate('shotImages(state.project.shots[0]).length'), 1);
  assert.equal(evaluate('shotImages(state.project.shots[0])[0].id'), 'render.png');
  evaluate(`state.mediaRole='reference';`);
  assert.equal(evaluate('filteredMedia().length'), 1);
  evaluate(`state.search='not-found';`);
  assert.equal(evaluate('filteredMedia().length'), 0);
  const graph = evaluate('relationsView()');
  assert.ok(graph.includes('Lien par nom de fichier'));
  assert.ok(graph.includes('/media/fixture/reference.png'));
});

test('document inspector renders untrusted artifact data as text', () => {
  const {evaluate, elements} = app();
  evaluate(`state.project={id:'fixture',artifacts:[{path:'story/story.yaml',kind:'story',valid:null,data:{logline:'</pre><script>evil()</script>'},errors:[]}]};showModal('artifact','story/story.yaml');`);
  const html = elements.get('#inspector-content').innerHTML;
  assert.ok(html.includes('&lt;/pre&gt;&lt;script&gt;'));
  assert.ok(!html.includes('<script>evil()'));
});

test('identity review is not asset or final-film approval', () => {
  const {evaluate} = app();
  const html = evaluate(`reviewBadges({identity_approved:true,production_final:false,film_final:false})`);
  assert.ok(html.includes('Identité approuvée'));
  assert.ok(html.includes('Approbation asset non renseignée'));
  assert.ok(!html.includes('Asset approuvé'));
  assert.ok(!html.includes('Final film documenté'));
  assert.ok(evaluate('reviewBadges({approved:false})').includes('Asset non approuvé'));
});

test('stage counts are escaped even if malformed on disk', () => {
  const {evaluate} = app();
  evaluate(`state.project={stages:[{label:'Scénario',status:'present',count:'<img src=x onerror=evil()>'}]};`);
  const html = evaluate('stageStrip()');
  assert.ok(!html.includes('<img'));
  assert.ok(html.includes('&lt;img'));
});

test('one-sided media IDs are usable in filters and graphs; unknown provenance stays unknown', () => {
  const {evaluate} = app();
  evaluate(`state.project={id:'fixture',scenes:[],shots:[{id:'shot_A',media_ids:['ref.png','render.png'],characters:[],prompts:[]}],entities:[],media:[{id:'ref.png',path:'ref.png',url:'/media/fixture/ref.png',kind:'image',role:'reference',shot_ids:[],entity_ids:[]},{id:'render.png',path:'render.png',url:'/media/fixture/render.png',kind:'image',role:'shot',shot_ids:[],entity_ids:[]}],artifacts:[]};state.shotFilter='shot_A';`);
  assert.equal(evaluate('filteredMedia().length'), 2);
  const html = evaluate('relationsView()');
  assert.ok(html.includes('/media/fixture/ref.png'));
  assert.ok(html.includes('Origine du lien inconnue'));
  assert.ok(!html.includes('Lien documenté'));
});

function configureResponses(ctx, project) {
  ctx.fetch = async url => ({ok: true, json: async () =>
    url === '/api/projects' ? {projects: project ? [{id:project.id,title:project.title}] : []} : project});
}
const fixture = () => ({id:'fixture',title:'Le film fixture',scenes:[],shots:[],media:[],entities:[],artifacts:[],stages:[],warnings:[]});

test('automatic refresh restores a project that disappears then reappears unchanged', async () => {
  const {ctx, evaluate, elements} = app();
  const project = fixture();
  configureResponses(ctx, project); await evaluate('refresh()');
  assert.ok(elements.get('#content').innerHTML.includes('Le film fixture'));
  configureResponses(ctx, null); await evaluate('refresh()');
  assert.ok(elements.get('#content').innerHTML.includes('attend son premier film'));
  configureResponses(ctx, project); await evaluate('refresh()');
  assert.ok(elements.get('#content').innerHTML.includes('Le film fixture'));
  assert.ok(!elements.get('#content').innerHTML.includes('attend son premier film'));
});

test('automatic refresh closes an inspector whose item disappeared', async () => {
  const {ctx, evaluate, elements} = app();
  const project = fixture();
  project.artifacts=[{path:'story/story.yaml',kind:'story',data:{title:'Fixture'},errors:[]}];
  configureResponses(ctx, project); await evaluate('refresh()');
  evaluate(`showModal('artifact','story/story.yaml')`);
  assert.ok(elements.get('#inspector').open);
  project.artifacts=[]; await evaluate('refresh()');
  assert.equal(elements.get('#inspector').open, false);
  assert.equal(elements.get('#inspector-content').innerHTML, '');
});

test('unrelated refresh does not recreate a media player in pause', async () => {
  const {ctx, evaluate, elements} = app();
  const project=fixture();
  project.media=[{id:'clip.mp4',path:'clip.mp4',url:'/media/fixture/clip.mp4',kind:'video',role:'unlinked',shot_ids:[],entity_ids:[]}];
  configureResponses(ctx,project); await evaluate('refresh()');
  evaluate(`showModal('media','clip.mp4')`);
  const original = elements.get('#inspector-content').innerHTML;
  const marker='<!-- player unchanged -->';
  elements.get('#inspector-content').innerHTML+=marker;
  project.warnings=['An unrelated document was modified']; await evaluate('refresh()');
  assert.equal(elements.get('#inspector-content').innerHTML, original+marker);
});

test('archived render is kept in history but not used as a shot thumbnail', () => {
  const {evaluate}=app();
  evaluate(`state.project={shots:[{id:'shot_A'}],media:[{id:'old.png',kind:'image',role:'shot',archived:true,shot_ids:['shot_A']}]};`);
  assert.equal(evaluate('shotMedia(state.project.shots[0]).length'), 1);
  assert.equal(evaluate('shotImages(state.project.shots[0]).length'), 0);
  assert.ok(evaluate('reviewBadges(state.project.media[0])').includes('ARCHIVÉ'));
});

test('a render used as input remains a source render, not a new render of the consumer', () => {
  const {evaluate}=app();
  evaluate(`state.project={shots:[{id:'shot_A',characters:[]},{id:'shot_B',characters:[]}],media:[{id:'source.png',path:'source.png',kind:'image',role:'shot',shot_ids:['shot_A'],relation:'filename',usage_records:[{path:'prompts/consumer.yaml',shot_ids:['shot_B'],relation:'explicit'}]}],entities:[]};state.shotFilter='shot_B';`);
  assert.equal(evaluate('shotImages(state.project.shots[0]).length'),1);
  assert.equal(evaluate('shotImages(state.project.shots[1]).length'),0);
  assert.equal(evaluate('shotReferences(state.project.shots[1]).length'),1);
  assert.equal(evaluate('filteredMedia().length'),1);
  assert.equal(evaluate('inputRelation(state.project.media[0],state.project.shots[1]).relation'),'explicit');
});

const productionFixture = () => ({id:'fixture',title:'Fixture',duration_seconds:20,
  stages:[{id:'story',label:'Histoire',phase:'writing',status:'present',count:1},{id:'screenplay',label:'Scénario',phase:'writing',status:'present',count:1},{id:'reference_sheets',label:'Planches',phase:'world',status:'present',count:2,documented_approvals:1},{id:'image_media',label:'Keyframes',phase:'images',status:'present',count:2},{id:'video_media',label:'Vidéos',phase:'motion',status:'missing',count:0}],
  scenes:[{id:'scene_A',title:'Scène A',number:1,shot_ids:['shot_1','shot_2']}],
  shots:[{id:'shot_1',scene_id:'scene_A',sequence:1,start_seconds:0,duration_seconds:8,needs_motion:true,prompts:[{path:'p1.yaml',kind:'image_prompt'},{path:'v1.yaml',kind:'video_prompt'}],characters:['char_A']},
         {id:'shot_2',scene_id:'scene_A',sequence:2,start_seconds:8,duration_seconds:6,needs_motion:false,prompts:[],characters:[]}],
  entities:[{id:'char_A',kind:'character',name:'char_A',media_ids:[]}],
  media:[{id:'renders/a.png',path:'renders/shot_1/4b8f21a1_000.png',url:'/media/fixture/a.png',kind:'image',role:'shot',shot_ids:['shot_1'],approved:true},
         {id:'renders/b.png',path:'renders/shot_2/b.png',url:'/media/fixture/b.png',kind:'image',role:'shot',shot_ids:['shot_2'],review_status:'rejected_geometry'},
         {id:'refs/sheet.png',path:'references/generated/char_A/attempt-01/aa11bb22_000.png',url:'/media/fixture/s.png',kind:'image',role:'reference',entity_ids:['char_A'],reference_approvals:[{path:'references/approved.yaml',approved_at:'2026-10-05',consent_verbatim:'oui',entity_id:'char_A',order:1}]},
         {id:'refs/front.png',path:'references/generated/char_A/attempt-01/crops/front.png',url:'/media/fixture/f.png',kind:'image',role:'reference',entity_ids:['char_A'],derived_from:'refs/sheet.png',view:'front'}],
  artifacts:[{path:'references/generated/char_A/attempt-01/review.md',kind:'note',data:'<b>Revue</b>'}],warnings:[],
  budget:{decision:{selected_tier:'preparation',max_spend_usd:30},ledger:{available:true,jobs:3,committed_usd:0.054,jobs_without_actual_cost:0}}});

test('production view: next stage, approvals, budget and shot board are derived honestly', () => {
  const {evaluate}=app();
  evaluate(`state.project=${JSON.stringify(productionFixture())};`);
  assert.equal(evaluate('nextStage().id'),'video_media');
  assert.equal(evaluate('shotProgress(state.project.shots[0]).keyframe'),'done');
  assert.equal(evaluate('shotProgress(state.project.shots[1]).keyframe'),'bad');
  assert.equal(evaluate('shotProgress(state.project.shots[1]).video'),'na');
  assert.equal(evaluate('shotProgress(state.project.shots[0]).video'),'todo');
  assert.equal(evaluate('shotLabel(state.project.shots[1])'),'S01 · P02');
  assert.equal(evaluate(`mediaLabel(state.project.media[0])`),'renders · shot_1');
  assert.equal(evaluate(`mediaLabel(state.project.media[3])`),'char_A · attempt-01 · front');
  const html=evaluate('productionView()');
  for(const expected of ['Où en est le film','Vidéos','0,054 $','30,00 $','S01 · P01','Timeline du film','1 approuvée au registre']) assert.ok(html.includes(expected),expected);
  assert.ok(!html.includes('undefined') && !html.includes('NaN'));
});

test('production view without shots shows an honest empty timeline and the visual bible', () => {
  const {evaluate}=app();
  const fixture=productionFixture();fixture.shots=[];fixture.scenes=[];
  evaluate(`state.project=${JSON.stringify(fixture)};`);
  const html=evaluate('productionView()');
  assert.ok(html.includes('le découpage en plans n’existe pas encore'));
  assert.ok(!html.includes('Tableau des plans'));
  assert.ok(html.includes('char_A'));
  assert.ok(evaluate('overviewView()').includes('La bible visuelle'));
});

test('notes are rendered as escaped plain text and derived views never show their own approval', () => {
  const {evaluate,elements}=app();
  evaluate(`state.project=${JSON.stringify(productionFixture())};showModal('artifact','references/generated/char_A/attempt-01/review.md');`);
  assert.ok(elements.get('#inspector-content').innerHTML.includes('&lt;b&gt;Revue'));
  evaluate(`showModal('media','refs/front.png')`);
  const html=elements.get('#inspector-content').innerHTML;
  assert.ok(html.includes('Vue dérivée'));
  assert.ok(!html.includes('Approbation documentée'));
  evaluate(`showModal('entity','char_A')`);
  assert.ok(elements.get('#inspector-content').innerHTML.includes('« oui »'));
});

test('storyboard view: panels by scene, drawings are not keyframes, scenes without panels show their brief', () => {
  const {evaluate,elements}=app();
  const fixture=productionFixture();
  fixture.scenes.push({id:'scene_B',title:'EXT. RUE — NUIT',number:2,characters:['char_A'],visual_intent:'Pluie <i>battante</i>',notes:['screenplay/scene_B.md'],shot_ids:[]});
  fixture.panels=[{id:'panel_1',scene_id:'scene_A',shot_id:'shot_1',order:1,composition:'Plan large',camera:'Travelling avant',action:'Il entre',media_ids:['sb/panel_1.png'],characters:['char_A'],source:'storyboard/storyboard.yaml'},
                  {id:'panel_2',scene_id:'scene_A',shot_id:'shot_x',order:2,composition:'Gros plan <b>',media_ids:[],source:'storyboard/storyboard.yaml'}];
  fixture.media.push({id:'sb/panel_1.png',path:'storyboard/panel_1.png',url:'/media/fixture/sb.png',kind:'image',role:'storyboard',shot_ids:['shot_1'],panel_ids:['panel_1']});
  fixture.shots[0].media_ids=['sb/panel_1.png'];
  evaluate(`state.project=${JSON.stringify(fixture)};`);
  const html=evaluate('storyboardView()');
  for(const expected of ['Le film, case par case','STORYBOARD À FAIRE','Pluie &lt;i&gt;battante&lt;/i&gt;','Gros plan &lt;b&gt;','CAM · Travelling avant','/media/fixture/sb.png','Lire la scène']) assert.ok(html.includes(expected),expected);
  assert.ok(!html.includes('undefined')&&!html.includes('NaN'));
  assert.equal(evaluate("shotImages(state.project.shots[0]).map(m=>m.id).join(',')"),'renders/a.png');
  evaluate(`showModal('panel','panel_2')`);
  const modal=elements.get('#inspector-content').innerHTML;
  assert.ok(modal.includes('pas encore dans la liste des plans'));
  assert.ok(modal.includes('ni une keyframe'));
  evaluate(`showModal('shot','shot_1')`);
  assert.ok(elements.get('#inspector-content').innerHTML.includes('<h3>Storyboard</h3>'));
});

test('storyboard view on an empty project stays honest', () => {
  const {evaluate}=app();
  evaluate(`state.project={id:'x',scenes:[],panels:[],shots:[],media:[],entities:[],artifacts:[],stages:[]};`);
  assert.ok(evaluate('storyboardView()').includes('Pas encore de scénario ni de storyboard'));
});

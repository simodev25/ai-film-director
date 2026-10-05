# Options des modèles ComfyUI — premier scan (trois gammes)

Scan **en lecture seule** du 2026-10-05 (étape 3 « Model options scan » de
`.opencode/skills/cloud-production/SKILL.md`). Aucune génération, aucune
installation, aucun téléchargement. Rien ici n'est une autorisation de dépense :
chaque option payante ou qui change la qualité doit être présentée à
l'utilisateur avec la demande de batch, puis acceptée explicitement
(`docs/cloud-policy.md`).

**Cible** : ComfyUI v0.38.2 sur `127.0.0.1:8188`, comfy-cli 1.22.0, packs
`openrouter-studio` 0.3.0 et `comfyui-openrouter` 615d52ab (à jour au
2026-10-05). Mac M4 Max, 36 Go de mémoire unifiée.

**Sources**
- Descripteurs des nœuds sauvegardés aujourd'hui (même version du plugin) :
  `projects/la-pomme/workflows/cloud/preparation/scene-01-video/node-catalog.selected.live.json`
  (`OpenRouterStudioVideo`) et
  `projects/la-pomme/workflows/cloud/tests/scene-01-shots/node-catalog.selected.live.json`
  (`OpenRouterStudioImage`).
- `nodes(action="get")` en direct pour `OpenRouterAudioSpeak`,
  `OpenRouterRequestOptions`, `ColorTransfer` et
  `FrameInterpolationModelLoader`. `nodes(action="search"/"list")` pour les
  nœuds locaux.
- Code du plugin : `openrouter_studio/{nodes,payloads,specs,catalog}.py` et
  `comfyui-openrouter/src/{nodes/audio/speak.py,openrouter/speech.py,openrouter/options.py}`.
- Requêtes GET publiques : `/api/v1/images/models`, `/api/v1/images/models/<id>/endpoints`,
  `/api/v1/videos/models` et la documentation TTS
  (`docs/guides/overview/multimodal/tts.md`).

**Légende de disponibilité**
- ✅ **disponible maintenant** : l'entrée existe dans le descripteur live **et**
  la chaîne projet (`scripts/cloud_batch.py` / `src/comfyui/cloud_adapters.py`) la
  mappe déjà.
- 🟡 **nœud prêt, câblage projet requis** : l'entrée existe dans le descripteur
  live, mais l'adaptateur ne la mappe pas encore. Il faut soit l'écrire en
  valeur fixe dans une **copie** du scaffold, soit ajouter la capacité dans
  `config/cloud-tiers.yaml` (par exemple `seed: true`). **Aucune installation.**
- 🔴 **installation requise** : il faut un pack de nœuds ou un fichier de
  modèle, et l'accord explicite de l'utilisateur.
- ⛔ **non supporté** par ce modèle ou cette route.

Style cible (`story/story.yaml`) : *manga sombre, anime 2D psychologique,
cellulo (CEL) des années 1990, contours noirs légèrement irréguliers, ombres
franches, fonds peints, grain discret, animation retenue.*

---

## Top 5 des options à activer pour La Pomme

| # | Option | Pourquoi | Coût | État |
|---|---|---|---|---|
| 1 | **Prompt négatif propre au style CEL** : Veo `model.special__negativePrompt` (Lite et 3.1). Pour Wan 3.0, le négatif est intégré au prompt sous `Avoid:` (`negative_fold`). | C'est le levier le plus direct contre la dérive vers la 3D, le photoréalisme, le morphing, le texte incrusté ou les ombres en dégradé. Le même texte de négatif sert aux trois gammes. | 0 $ | ✅ (`cloud_batch.py` choisit l'entrée live ou l'intégration au prompt) |
| 2 | **Images de référence Seedream 5.0 Flash en `resolution: 2K`** au lieu de 1K | Le prix est **le même : 0,018 $ par image**. Les fiches modèles et lieux gagnent en détail de trait, ce qui sert de meilleure source aux images-clés de test et de production comme à l'agrandissement. | 0 $ de plus par image (temps de génération un peu plus long) | ✅ (`2K` figure dans les capacités) — change la qualité, donc **à proposer à l'utilisateur** |
| 3 | **Première et dernière image sur Veo** (`model.first_frame` + `model.last_frame`) | Fixe la composition de départ et la pose d'arrivée. C'est la clé de la continuité entre les coupes et de la passe de montée en gamme. Wan 3.0 n'a que la première image : un plan qui doit atteindre un état final précis passe par Veo, ou il est découpé. | 0 $ de plus (facturation à la seconde) | ✅ (rôles `first_frame` / `last_frame`) |
| 4 | **Retouche ciblée par Nano Banana 2 ou Pro, puis composite masqué local** : image-clé approuvée en `reference_1`, fiche modèle en `reference_2`, consigne « ne changer que X », puis `ImageCompositeMasked` + `FeatherMask`/`GrowMask` pour ne garder que la zone corrigée. | Corrige la continuité (accessoire, œil, oreille du chat) **sans re-mettre en scène le plan**. Les pixels hors masque restent identiques. | 1 image : 0,067 $ (Nano Banana 2, 1K) ou 0,134 $ (Pro, 2K), plus 0,0006 à 0,0011 $ par référence. Le composite est gratuit. | ✅ côté nœuds (Studio + nœuds de masque du cœur). Le masque est dessiné à la main dans l'éditeur Studio (`OpenRouterStudioAsset`) ou chargé. |
| 5 | **Correspondance des couleurs locale `ColorTransfer`** (`mkl_lab` ou `reinhard_lab`, `source_stats: uniform`, `strength` 0,6–1,0) entre les images des clips et l'image-clé approuvée | Rattrape la dérive de palette de Veo et Wan, et l'écart entre les gammes. `uniform` applique la même correction à toutes les images, ce qui évite le scintillement. | 0 $ (traitement local CPU/MPS) | ✅ (nœuds du cœur : `LoadVideo` → `GetVideoComponents` → `ColorTransfer` → `CreateVideo` → `SaveVideo`) |

Ensuite, par ordre d'intérêt :
- **Seed** sur Veo, Wan et Seedream (🟡, il faut ajouter `seed: true` dans les
  capacités de la config) pour reproduire une prise.
- **`enhancePrompt: false`** sur Veo (🟡, valeur fixe dans le graphe ; effet à
  vérifier) pour que Google ne réécrive pas un prompt de continuité structuré.
- **Épingler `provider_route`** sur les modèles Gemini (🟡).

---

## Réglages communs des nœuds OpenRouter Studio (images et vidéos)

| Option | Effet | Recommandation | Coût | État |
|---|---|---|---|---|
| `strict_validation` | Rejette avant l'envoi les valeurs non annoncées, les clés de fournisseur hors liste autorisée et les combinaisons impossibles (`last_frame` sans `first_frame`, images de cadre + `input_references`). | **true**, toujours | Évite des échecs qui pourraient être facturés | ✅ |
| `reference_max_megapixels` | Réduit la taille des références et des cadres avant l'encodage PNG en base64. Défaut : 16 Mpx (image) et 12 Mpx (vidéo). | Laisser le défaut. Descendre à ~4 Mpx seulement si l'envoi est trop lourd. | Négligeable : les références Gemini sont facturées en jetons, à peu près par image | ✅ |
| `rerun_nonce` | Contourne le cache de ComfyUI pour relancer **le même** graphe. | Le changer uniquement pour une nouvelle tentative **approuvée** : c'est un nouveau tirage payant. | = 1 génération | ✅ |
| `studio_reference_manifest` | Traçabilité des références dans l'interface Studio. | Laisser vide (le projet a son propre registre). | 0 | ✅ |
| `save_raw_artifacts` (image) | Conserve les octets bruts renvoyés par le fournisseur. | **true**, pour la provenance | 0 | ✅ |
| `request_timeout_seconds` (image) | Délai maximal de la requête. | 600 | 0 | ✅ |
| `poll_interval_seconds` / `poll_timeout_seconds` / `callback_url` (vidéo) | Suivi de la tâche. `callback_url` doit être en HTTPS. | 5 s / 3600 s / vide | 0 | ✅ |
| `OpenRouterStudioResumeVideo` (nœud) | Reprend une tâche vidéo interrompue d'après son identifiant fournisseur enregistré, **sans renvoyer de requête de génération**. | À utiliser en cas de coupure au lieu de relancer. | Évite une double facturation | ✅ (nœud installé, pas encore câblé dans `cloud_batch`) |

À savoir : le plugin **ne relance jamais** le POST de génération (0
nouvelle tentative). Seules les vérifications d'état sont répétées (3 fois).
Sorties disponibles : média, image d'affiche (la **première** image décodée),
identifiants de tâche, métadonnées, coût estimé et coût réel.

---

## Images — nœud `OpenRouterStudioImage`

### Préparation — `bytedance-seed/seedream-5-0-flash` (fournisseur unique `seed`)

| Option | Effet | Recommandation CEL sombre | Coût | État |
|---|---|---|---|---|
| `model.prompt` | Consigne obligatoire, même quand des références sont branchées. Les raccourcis `@image_ref1`, `@image_ref2`… sont convertis en « the first/second reference image ». | Style en tête, puis sujet, puis consignes de conservation. Désigner les références par leur ordre. | — | ✅ |
| `model.resolution` | `1K` ou `2K`, ou défaut du fournisseur | **2K** pour les fiches modèles et les lieux ; 1K pour les ébauches | **0,018 $ dans les deux cas** | ✅ |
| `model.aspect_ratio` | 18 valeurs, dont `16:9`, `21:9`, `9:16`, `1:1`, `auto` | `16:9` pour les plans ; `1:1` ou `3:2` pour les planches de personnage | 0 | ✅ (16:9, 9:16 et 1:1 dans les capacités) |
| `model.size` | Taille exacte `LxH` ou `2K` ; **prioritaire** : supprime résolution et format | Laisser vide | 0 | 🟡 |
| `model.seed` | Annoncé par le catalogue (`seed: boolean`). La valeur −1 l'omet. | Fixer une valeur par planche pour pouvoir refaire une variation | 0 | 🟡 (capacités de la config sans `seed`) |
| `model.reference_images` (`reference_1`…`reference_14`) | Références ordonnées, de 0 à 14 | Fiche du personnage, puis fiche du lieu, puis planche de style. Au maximum 3 à 5 références utiles. | **Références gratuites** sur cette gamme | ✅ |
| `model.n` | Nombre d'images, fixé à 1 | 1 | — | ✅ |
| `model.provider_options_json` | Options de fournisseur brutes. **Liste d'options autorisées vide** : en mode strict, toute clé est rejetée. | Vide | — | ⛔ |
| `provider_route` / `allow_fallbacks` / `provider_sort` | Absents : un seul fournisseur, et pas de détail de point d'accès dans l'instantané du plugin | — | — | ⛔ |
| Prompt négatif | Aucune entrée. Le négatif est donc **intégré au prompt** (« Avoid: … »). | « Avoid: 3D render, CGI, photorealism, glossy airbrushed shading, soft gradient shadows, bloom, lens flare, text, watermark, extra limbs » | 0 | ✅ (intégration au prompt) |

### Tests — `google/gemini-3.1-flash-image` (Nano Banana 2)

| Option | Effet | Recommandation CEL sombre | Coût | État |
|---|---|---|---|---|
| `model.prompt` | Comme ci-dessus. Le modèle est bon en **retouche multi-références** : « même personnage, nouvel angle » ou « ne changer que X ». | Consigne de retouche courte et ciblée, plus « keep linework, flat cel shading, hard shadows unchanged » | — | ✅ |
| `model.resolution` | `512`, `1K`, `2K`, `4K` | **1K** (gamme tests). `512` pour une planche contact rapide. | Estimations à 6e-5 $ par jeton de sortie : 1K ≈ **0,067 $** · 2K ≈ 0,101 $ · 4K ≈ 0,151 $ · 512 : ≈ 0,045 $, à vérifier | ✅ (`512` absent des capacités de la config : 🟡) |
| `model.aspect_ratio` | 14 valeurs (de `1:8` à `8:1`, dont `21:9`) | `16:9` | 0 | ✅ |
| `model.size` | Taille exacte (prioritaire) | Vide | 0 | 🟡 |
| `model.reference_images` | De 0 à 14, dans l'ordre | Image-clé ou fiche modèle d'abord, lieu ensuite | ≈ **0,00056 $ par référence** | ✅ |
| Seed | **Non annoncé** : aucune reproductibilité. La seule façon de faire varier est `rerun_nonce`. | — | — | ⛔ |
| `model.provider_route` | `automatic routing`, `google-vertex/global` ou `google-ai-studio` | Épingler **une** route pour toute une série d'images, par souci de cohérence | 0 | 🟡 (valeur fixe dans le graphe) |
| `model.allow_fallbacks` | Autorise ou non le basculement vers une autre route | `false` si une route est épinglée (pas de changement silencieux) | 0 | 🟡 |
| `model.provider_sort` | `price`, `throughput` ou `latency` | Défaut du fournisseur | 0 | 🟡 |
| `model.special__cachedContent` | Nom d'une ressource de cache Gemini, qui ne se crée pas via OpenRouter | Vide | — | ⛔ (inutilisable ici) |
| `model.provider_options_json` | Seule clé autorisée : `cachedContent` | Vide | — | ⛔ |
| Prompt négatif | Aucune entrée : intégration au prompt | Même texte que pour Seedream | 0 | ✅ |

### Production — `google/gemini-3-pro-image` (Nano Banana Pro)

Mêmes entrées que Nano Banana 2, avec quelques différences :

| Option | Différence ou point clé | Recommandation | Coût | État |
|---|---|---|---|---|
| `model.resolution` | `1K`, `2K`, `4K`. **Sur la route Vertex, seulement 1K et 2K** : le 4K exige `google-ai-studio/global`. | **2K** (défaut de la gamme). Le 4K seulement pour une image-titre, et avec la route épinglée. | 1K et 2K ≈ **0,1344 $** (même nombre de jetons) · 4K ≈ 0,24 $ (estimation) | ✅ 2K · 🟡 4K + route |
| `model.provider_route` | `google-vertex/global` ou `google-ai-studio/global` | Épingler la même route que pour la passe de montée en gamme | 0 | 🟡 |
| `model.reference_images` | De 0 à 14 | Image-clé approuvée (composition) + mêmes vues de fiche modèle (`docs/film-method.md`, montée en gamme) | ≈ **0,00112 $ par référence** | ✅ |
| `model.aspect_ratio` | 10 valeurs, sans `1:4` ni `8:1` | `16:9` | 0 | ✅ |
| Seed | Non annoncé | — | — | ⛔ |

---

## Vidéos — nœud `OpenRouterStudioVideo`

Règles du plugin, valables pour les trois modèles :
- `size` exact est prioritaire sur `resolution` + `aspect_ratio`.
- `last_frame` exige `first_frame` en mode strict.
- En mode strict, il est **interdit de combiner** des images de cadre
  (`first_frame`/`last_frame`) et des `reference_images` ou `remote_references_json`.
- Le prompt est limité à 10 000 caractères.
- Les valeurs `special__*` sont envoyées dans `provider.options.<slug>.parameters`.
  Pour Veo, l'identifiant résolu est `google-vertex`.

### Préparation — `google/veo-3.1-lite`

| Option | Effet | Recommandation CEL sombre | Coût | État |
|---|---|---|---|---|
| `model.prompt` | Mise en scène, mouvement, caméra | Un seul mouvement principal, caméra retenue, « limited animation, held poses » | — | ✅ |
| `model.duration` | 4, 6 ou 8 s | Selon le découpage ; préférer 4 ou 6 s pour les plans tenus | Proportionnel à la durée | ✅ |
| `model.resolution` | `720p` ou `1080p` | **720p** | 720p **0,03 $/s** · 1080p 0,05 $/s (sans son) | ✅ |
| `model.size` | `1280x720`, `1920x1080`, `720x1280` ou `1080x1920`, ou défaut | Défaut du fournisseur (`resolution` + format suffisent) | 0 | 🟡 |
| `model.aspect_ratio` | `16:9` ou `9:16` | `16:9` (valeur fixe dans le scaffold) | 0 | 🟡 (la config n'a pas de formats vidéo) |
| `model.generate_audio` | Son natif | **false** (son réalisé à part) | +0,02 $/s (720p : 0,05 contre 0,03) | ✅ (false imposé) |
| `model.seed` | Annoncé (`seed: true`) ; −1 l'omet | Fixer une valeur par plan pour pouvoir refaire une prise (reproductibilité non garantie par Google) | 0 | 🟡 (ajouter `seed: true` dans les capacités) |
| `model.first_frame` / `model.last_frame` | Une image chacun ; la dernière exige la première | **Les deux** dès qu'une pose d'arrivée compte (image-clé N → image-clé N+1) | 0 | ✅ |
| `model.reference_images` (de 0 à 9 dans le plugin) | Images de guidage (sujet, style). **Incompatible avec les cadres** en mode strict. Limite du fournisseur non publiée sur OpenRouter. | À n'utiliser que pour un plan sans cadre de départ, ce qui est rare | Pas de tarif de référence publié | 🟡 (l'adaptateur refuse le mélange : comportement voulu) |
| `model.remote_references_json` | Références `input_references` par URL HTTPS | Vide (les références restent locales et versionnées) | — | ⛔ par choix |
| `model.special__negativePrompt` | Prompt négatif natif de Google | **Activer** : « 3D render, CGI, photorealistic skin, smooth gradient shading, morphing, warping faces, extra limbs, flicker, camera shake, text, subtitles, watermark, lens flare, bloom » | 0 | ✅ |
| `model.special__enhancePrompt` | Google réécrit ou enrichit le prompt | **false**, pour garder la continuité et la sobriété. Effet à confirmer sur un clip : Google peut ignorer la valeur. | 0 | 🟡 |
| `model.special__personGeneration` | Règle Google sur les personnes (`allow_adult`, `dont_allow`…) | **Défaut du fournisseur**. Ne pas mettre `dont_allow`/`disallow`, qui bloquerait Marc. `allow_adult` risque de refuser Marc à 7 ans (souvenir de 1993). En cas de refus, ne pas relancer en boucle. | Un refus peut être facturé | 🟡 |
| `model.special__conditioningScale` | Force du conditionnement par l'image ; la plage n'est pas publiée | Vide (défaut). À tester seulement si un clip s'écarte trop de l'image-clé. | 0 | 🟡 (non testé) |
| `model.special__aspectRatio` | Format imposé côté fournisseur, en double avec le contrôle normalisé | Défaut du fournisseur (risque de conflit) | 0 | 🟡 |
| `model.provider_options_json` | JSON brut, limité à la liste autorisée (les 5 clés ci-dessus) | Vide : passer par les contrôles `special__*` | 0 | 🟡 |

### Tests — `alibaba/wan-3.0`

| Option | Effet | Recommandation CEL sombre | Coût | État |
|---|---|---|---|---|
| `model.prompt` | Jusqu'à 10 000 caractères. Le négatif y est intégré sous `Avoid:`. | Même texte de négatif que pour Veo, intégré au prompt | — | ✅ |
| `model.duration` | Entier de **2 à 30 s** | La durée exacte du plan (pas d'arrondi à 4/6/8) : on paie moins et on coupe moins au montage | Proportionnel à la durée | ✅ |
| `model.resolution` | `480p`, `720p` ou `1080p` (défaut du nœud : **480p**, à toujours fixer) | **720p** (choix de l'utilisateur). Le 480p pour une animatique = choix explicite seulement. | 480p 0,05 · **720p 0,10** · 1080p 0,20 $/s | ✅ |
| `model.aspect_ratio` | `16:9`, `4:3`, `1:1`, `3:4`, `9:16` | `16:9` | 0 | 🟡 (valeur fixe) |
| `model.generate_audio` | Son natif | **false**. `true` n'a **pas de tarif** et reste bloqué. | Inconnu | ✅ (false) |
| `model.seed` | Annoncé (`seed: true`) | Fixer une valeur par plan | 0 | 🟡 |
| `model.first_frame` | **Seule** image de cadre : pas de `last_frame` | Image-clé Nano Banana 2 approuvée | 0 | ✅ |
| `model.size` / `last_frame` / `reference_images` / `special__*` | **Absents** : pas de taille exacte, pas de prompt négatif natif, liste d'options autorisées vide | — | — | ⛔ |
| `model.remote_references_json` | Présent, mais l'architecture du catalogue est vide : refusé en mode strict, et interdit avec `first_frame` | Vide | — | ⛔ |
| `model.provider_options_json` | Liste d'options autorisées vide | Vide | — | ⛔ |

### Production — `google/veo-3.1`

Mêmes entrées que Veo 3.1 Lite (`special__negativePrompt`, `enhancePrompt`,
`personGeneration`, `conditioningScale`, `aspectRatio`, cadres, références,
seed), avec quelques différences :

| Option | Différence | Recommandation | Coût | État |
|---|---|---|---|---|
| `model.resolution` | `720p`, `1080p`, `4K` | **1080p** (défaut de la gamme). Le 4K n'apporte rien pour un rendu cellulo et coûte le double. | 720p/1080p **0,20 $/s** · 4K 0,40 $/s (sans son) | ✅ |
| `model.size` | Ajoute `3840x2160` et `2160x3840` | Défaut du fournisseur | 0 | 🟡 |
| `model.generate_audio` | Son natif | **false** | +0,20 $/s (0,40 $/s ; 0,60 $/s en 4K) | ✅ (false) |
| Cadres | Image-clé de production en première image, et en dernière si la pose d'arrivée a été approuvée en préparation | Rejouer **les mêmes** plans (montée en gamme) | 0 | ✅ |

---

## Audio — nœud `OpenRouterAudioSpeak` (`comfyui-openrouter`), modèle `bytedance-seed/seed-audio-1-0`

Route `/api/v1/audio/speech`, identique dans les trois gammes. Seed Audio
traite `input` comme un **prompt** : bruitages, ambiances ou scène sonore sans
parole.

| Option | Effet | Recommandation (film sans parole) | Coût | État |
|---|---|---|---|---|
| `model` (texte libre) | Identifiant OpenRouter | `bytedance-seed/seed-audio-1-0` | — | ✅ |
| `text` | Prompt (3000 caractères au maximum). La durée se pilote **uniquement par le texte**. | Durée exacte, « isolated foley, silent background, no voice, no music » (voir `prompts/audio/seed-audio-1-0/`) | Facturé à la durée **renvoyée** | ✅ |
| `voice` | Identifiant de voix Seed. Si vide, rien n'est envoyé. | **Vide** (obligatoire pour des bruitages ; un conflit avec les références provoque une erreur 400) | — | ✅ |
| `audio_format` | `pcm` ou `mp3` | **pcm** (sans perte ; rééchantillonnage en 48 kHz au montage) | 0 | ✅ |
| `speed` | De 0,5 à 2,0 pour Seed. Une valeur différente de 1,0 est envoyée. | **1.0** | 0 | ✅ |
| `voice_sample` (+ `sample_transcript`) | Envoyé en `input_references` comme voix de référence. Seed ignore la transcription. | Ne pas brancher pour des bruitages. Usage expérimental possible : un ronronnement de référence pour la cohérence de Nox, non vérifié. | 0 (durée de sortie seulement) | ✅ / non testé |
| `run_number` | Contourne le cache pour un nouveau tirage | Le changer uniquement pour une tentative approuvée | 1 génération | ✅ |
| `options` ← `OpenRouterRequestOptions` | `zdr`, `data_collection`, `extra_fields`. Le routage (`only`, `ignore`, `sort`) **n'est pas appliqué** à la parole. **Seed n'accepte aucune option de fournisseur.** | Ne rien brancher | 0 | ✅ (inutile) |
| Seed / durée / image de référence | Absents du nœud (`has_seed=False`). L'image `input_references` (conception de voix) n'est pas exposée. | Couper à la durée exacte au montage | Plafond de 120 s par requête, soit 0,30 $ au maximum | ⛔ |

Tarif : **0,0025 $ par seconde générée**. Un échec peut être facturé, et le
coût réel reste inconnu (`null`) tant qu'il n'est pas rapporté.

---

## Améliorations locales

Contexte : Mac M4 Max avec 36 Go de mémoire unifiée. La génération d'images en
local est possible (≥ 32 Go). **Pas de diffusion vidéo locale** : c'est la règle
du GPU Apple et de la politique du projet. Tout ce qui suit est du
post-traitement CPU/MPS, gratuit en argent.

### Déjà installé (nœuds du cœur de ComfyUI ou packs présents)

| Besoin | Nœuds | Usage pour La Pomme | État |
|---|---|---|---|
| Couleur | `ColorTransfer` (`reinhard_lab`, `mkl_lab` ou `histogram` ; `per_frame`, `uniform` ou `target_frame` ; `strength`), `ImageColorSpace`, `NormalizeImages`, `ImageInvert` | Caler les clips et les images sur la palette de l'image-clé approuvée ; `uniform` sur une vidéo pour éviter le scintillement | ✅ |
| Grain et texture | `ImageAddNoise`, `ImageBlur`, `ImageSharpen`, `ImageBlend`, `ImageQuantize`, `Morphology`, `Canny` | Grain discret uniforme sur tout le film (après toute IA) ; netteté légère des contours ; `Canny` pour extraire le trait d'une image-clé et le donner en référence de composition. `ImageQuantize` (aplats) avec prudence. | ✅ |
| Masques et composite | `ImageCompositeMasked`, `MaskComposite`, `FeatherMask`, `GrowMask`, `CropMask`, `InvertMask`, `ImageCropToMask`, `ImageToMask`, `ImageColorToMask`, `LoadImageMask`, `MediaPipeFaceMask` ; `SAM3_TrackToMask` (le modèle de détection n'est pas présent) | Retouche ciblée : ne recoller que la zone corrigée par Nano Banana (top 5, n° 4) | ✅ (SAM3 : 🔴 modèle) |
| Édition d'image dans le nuage (même route OpenRouter) | `OpenRouterStudioImage` avec Nano Banana 2 ou Pro, plusieurs références ; éditeur Studio (rognage, calques, masque peint) → `OpenRouterStudioAsset` (sorties `IMAGE` et `MASK`) | « Même personnage, nouvel angle », correction de continuité. L'API ne prend pas de masque : la précision vient du composite local. | ✅ (payant à l'image) |
| Agrandissement simple | `ImageScale` et `ImageScaleBy` (lanczos ou bicubique) | Passer de 720p à 1080p pour une maquette ; sans IA, donc trait un peu doux | ✅ |
| Agrandissement par modèle | `UpscaleModelLoader` + `ImageUpscaleWithModel` | Le nœud existe, mais **`models/upscale_models` est vide** | 🔴 modèle (voir ci-dessous) |
| Interpolation d'images | `FrameInterpolationModelLoader` + `FrameInterpolate` (cœur) | Le nœud existe, mais **`models/frame_interpolation` est vide** | 🔴 modèle |
| Vidéo | `LoadVideo`, `GetVideoComponents`, `CreateVideo`, `SaveVideo`, `SaveWEBM`, `VideoTrim`, `Video Slice`, `VideoCrop`, `VideoFrameSample`, `ConcatenateVideo` | Extraire la dernière image (`ImageFromBatch` −1), couper à la durée exacte, assembler | ✅ |
| Nœuds partenaires payants (crédits Comfy, **hors politique OpenRouter**) | `FluxVideoUpscaleNode`, `WavespeedFlashVSRNode`, `ByteDanceVideoEnhanceNode` (agrandissement et interpolation), `RecraftCrispUpscaleNode`, `Magnific*`, `Bria*` | Ils existent, mais sont facturés sur un autre compte et passent par une autre route. Ne pas les utiliser sans un choix explicite et une mise à jour de la politique. | ⛔ politique |

### Nécessiterait une installation (accord explicite obligatoire)

| Extension | Apport | Faisabilité sur M4 Max 36 Go | Priorité La Pomme |
|---|---|---|---|
| **Modèle d'agrandissement orienté anime** (fichier dans `models/upscale_models`, par exemple de la famille Real-ESRGAN anime ou AnimeSharp ; URL à choisir et vérifier) | Passage de 720p à 1080p, ou de 1080p à 4K, en gardant un trait net. Utilise **les nœuds du cœur déjà présents** : aucun pack à installer. | ✅ Images : quelques secondes chacune. Vidéo : de l'ordre de 0,5 à 2 s par image en 1080p via MPS, soit quelques minutes par clip de 8 s (estimation). | **Haute** (finition de la production, alternative au 4K payant) |
| **Modèle d'interpolation RIFE ou FILM** (fichier dans `models/frame_interpolation`, nœuds du cœur) ou pack `ComfyUI-Frame-Interpolation` | Plus d'images par seconde, ralentis | ✅ RIFE rapide, FILM plus lent | **Basse** : lisser va à l'encontre de l'animation limitée cellulo (images tenues). À réserver aux panoramiques. |
| **ComfyUI-VideoHelperSuite** | Chargement et assemblage vidéo avancés, aperçus | ✅ (ffmpeg absent du système : passer par `imageio-ffmpeg`) | Basse : le cœur couvre déjà le chargement, la création et l'enregistrement |
| **KJNodes** | Lots d'images, `ColorMatch`, `GrowMaskWithBlur`, grilles et concaténation (pratique pour la **planche contact 3×3** de `docs/film-method.md`) | ✅ CPU/MPS | Moyenne |
| **Post-production pellicule ou LUT** (pack de type ProPostProcessing : grain, LUT `.cube`, vignettage ; identifiant de registre à vérifier) | LUT unique pour tout le film, grain plus crédible qu'`ImageAddNoise` | ✅ CPU | Moyenne (finition) |
| **Préprocesseurs ControlNet** (`comfyui_controlnet_aux` : trait, profondeur) | Cartes de trait ou de profondeur d'une image-clé, à donner **en référence** à Nano Banana ou Seedream | ✅ (préprocesseurs seulement) | Moyenne. Le ControlNet complet, lui, exige une diffusion d'image locale (route ancienne, hors gammes). |
| **IPAdapter** (`ComfyUI_IPAdapter_plus`) | Identité et style par l'image pour une diffusion locale SD/SDXL | ⚠️ Possible pour des images seulement (≥ 32 Go), mais exige un modèle de diffusion local et une route hors gammes | Basse |

Chemin d'installation, si l'utilisateur l'accepte : `workflow_deps` →
`install_node` → `restart_comfyui` → `validate_workflow`. Pour un modèle :
`download_model` (+ `download(action="wait")`). Rien n'a été installé.

---

## Ce qu'il faut câbler côté projet (sans installation)

1. Ajouter `seed: true` aux capacités vidéo (Veo Lite, Wan 3.0, Veo 3.1) et à
   l'image Seedream, si l'utilisateur veut des prises reproductibles. Les
   capacités sont confirmées par le catalogue public du 2026-10-05.
2. Permettre dans `cloud_batch.py` des valeurs fixes pour les entrées
   `special__*` de Veo, autres que le négatif (`enhancePrompt`,
   `personGeneration`, `conditioningScale`), et pour `provider_route` /
   `allow_fallbacks` sur Gemini, sans toucher au graphe source.
3. Câbler `OpenRouterStudioResumeVideo` pour reprendre une tâche sans la
   soumettre une seconde fois.

À refaire dès que le modèle, la version du plugin ou la gamme change.

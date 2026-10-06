# La Pomme — complément de revue budgétaire

**Planification uniquement, aucune dépense autorisée.** Titre et durée restent
des propositions. Aucun choix de gamme/plafond, aucune approbation et aucun
`decision.yaml` n'ont été enregistrés. Scope : `planning_only_not_spend_consent`.

## Origine et validation

Documents lus : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`,
`docs/film-method.md` ; compétence `budget-estimation` chargée. Histoire canonique :
`story_la_pomme`, projet : `project_la_pomme`, 420 s, trois actes et douze beats.
Salon introspectif, adulte et sa version enfant (même identité), deux chats
distincts, parents hors champ : aucun artefact narratif ni ID n'a été changé.

Le script console `film-director` n'est pas installé dans le PATH. Son véritable
point d'entrée déclaré dans `pyproject.toml` est `cli:main` ; aides CLI inspectées,
puis même CLI exécutée sans installation :

```sh
PYTHONPATH=src /usr/local/bin/python3 -m cli budget projects/la-pomme \
  --assumptions projects/la-pomme/budget/assumptions.yaml
```

`project.yaml`, `story/story.yaml`, `budget/assumptions.yaml` et le fichier produit
`budget/estimate.yaml` ont été validés contre leurs schémas via
`validation.validate_file`, avec vérification des formats et résolution locale
des références de schéma. Les totaux/modèles ont aussi été revérifiés par
`budget_state` : `estimated: true`, `reviewed: false`, `awaiting_user_review`.

SHA-256 des **octets du YAML sauvegardé** (non modifié après génération) :

```text
afb4abb27306a20b7882ef6797ab890978dae2da37ff69ee192f6ca1f5b7abf6
```

Projet préexistant, revue initialement manquante ; aucun scénario n'existe dans ce
projet, donc le champ CLI `retrospective` vaut `false`. Aucun artefact canonique
existant n'a été réécrit. Le passage au scénario reste bloqué par la revue manquante.

## Hypothèses identiques pour les trois gammes

- Film proposé : **7 minutes = 420 s** ; proposition de **70 futurs plans/clips de
  6 s**, à action simple, et non quelques renders longs. Aucun shot ID actif créé.
- `images: 82` = **70 keyframes de plans + provision de 12 illustrations de
  modèles/références** (personnages/poses, lieu/angles et accessoires/états à
  répartir ultérieurement). Les 12 ne sont ni des références approuvées, ni 12
  entités nouvelles, ni des IDs actifs. Leur suffisance devra être revue après
  conception des personnages, art direction et découpage.
- `references_per_image: 3` = moyenne forfaitaire de **références en entrée** pour
  chaque image, soit 246 usages facturables d'inputs par passe dans ce calcul.
  Ce n'est pas 246 illustrations supplémentaires. Les mêmes fichiers/vues pourront
  être réutilisés. Les premiers model sheets n'auront pas nécessairement trois
  inputs ; le schéma ne permet pas une distribution distincte par catégorie,
  d'où ce forfait commun explicite. Aucun fichier de référence n'est déclaré prêt.
- Vidéo : `video_fraction: 1.0`, 420 s par passe, **sans audio natif**.
- Aucune réplique obligatoire, aucune narration et **0 s de parole/TTS**.
  `audio_seconds: 60` réserve seulement **60 s de sons isolés NON verbaux** Seed
  Audio, pas 420 s de bande-son finale. Le schéma ne distingue pas parole et sons ;
  cette précision est donc consignée ici, pas dans un champ inventé. Ambiances,
  room tone, bruitages discrets et transitions devront être composés en plusieurs
  couches locales/procédurales ou issues de sources existantes à provenance vérifiée.
  Si ces jobs Seed sont supprimés au profit du local, fixer `audio_seconds: 0`
  dans une nouvelle estimation et demander une nouvelle revue.
- Texte : **100 000 tokens input + 20 000 output** sur l'ensemble de la préparation
  (conception, prompts et corrections), enveloppe théorique et non mesure du travail
  déjà réalisé. Hypothèse de contexte standard **inférieur à 272 000 tokens** par
  appel ; pas de tarif extrapolé pour contexte long. Le prix du raisonnement demeure
  inconnu/exclu. Les recommandations texte config ne changent pas le LLM OpenCode
  hérité et ne constituent pas sa facture observée.
- Reprises : multiplicateurs de volume **1 / 1,25 / 1,75**, soit **0 % / 25 % / 75 %**
  supplémentaires dans les cas bas/moyen/haut. Le CLI applique ces multiplicateurs
  à tous les postes, texte compris. Ce sont des moyennes de volume, pas des nombres
  fractionnaires de tentatives par job, ni une moyenne statistique empirique.
- **Réserve supplémentaire de 10 %** sur chaque sous-total après reprises : marge
  comptable explicite distincte des reprises, pas plafond utilisateur ni garantie.
  Aucun retry n'est exécuté ou autorisé par ces hypothèses.

### Limite de comptage des clips dans le CLI

Le schéma ne possède pas d'entrée `shot_count` ou `clip_seconds`. L'estimateur
remplit automatiquement avec la durée **maximale** du modèle : il écrit **53 clips**
pour préparation/production (52 × 8 s + 4 s), et **14 clips** pour tests (14 × 30 s).
Ce sont des agrégats techniques, **pas le futur découpage**. La proposition réelle
de planification est **70 × 6 s dans chaque gamme**, compatible avec toutes les
caps, et facture aussi **420 s** : aucun arrondi supplémentaire ici, donc les coûts
à la seconde restent identiques. Les nombres de jobs, références de démarrage,
marges de raccord et toute éventuelle facturation minimale par appel devront être
revus après les shots. Ne pas lire les 14 agrégats comme une permission de longs
plans : la méthode conserve les actions courtes. Le YAML CLI est conservé intact.

## Coûts exacts du YAML, en USD

Totaux avec reprises et réserve de 10 %, **trois alternatives pour le même film**,
pas trois passes à lancer ni un budget cumulatif de montée en gamme :

| Gamme | Bas | Moyen | Haut |
|---|---:|---:|---:|
| préparation | 15,670600 | 19,588250 | 27,423550 |
| tests | 52,742976 | 65,928720 | 92,300208 |
| production | 105,430952 | 131,788690 | 184,504166 |

Le Markdown CLI arrondit son tableau à quatre décimales ; les nombres ci-dessus
reprennent les valeurs enregistrées à six décimales, non un devis à cette précision.

### Première passe, avant reprises et réserve

| Poste | Préparation | Tests | Production |
|---|---:|---:|---:|
| Texte théorique | 0,020000 | 0,150000 | 0,400000 |
| 70 images de plans, inputs inclus | 1,260000 | 4,821600 | 9,643200 |
| 12 illustrations provisionnelles, inputs inclus | 0,216000 | 0,826560 | 1,653120 |
| Total images (82) | 1,476000 | 5,648160 | 11,296320 |
| Vidéo 420 s | 12,600000 | 42,000000 | 84,000000 |
| Sons isolés 60 s | 0,150000 | 0,150000 | 0,150000 |
| Sous-total (sans double compter les lignes images) | 14,246000 | 47,948160 | 95,846320 |

Formule : `total = sous-total première passe × multiplicateur × 1,10`.
Images : `82 × (tarif output + 3 × tarif input référence)`.
La charge de références incluse dans le total images est **0 / 0,137760 / 0,275520 $**
par passe. En préparation seul l'input référence est sans supplément dans ce profil ;
**l'image générée n'est pas gratuite**. Prix unitaires images inputs inclus :
0,018 / 0,06888 / 0,13776 $. Le coût Google est dérivé des tokens, non un forfait
contractuel garanti ; la tokenisation réelle des images peut varier.

## Modèles, réglages et caps de la config

| Gamme | Texte recommandé | Image | Vidéo | Résolutions image / vidéo |
|---|---|---|---|---|
| préparation | `openai/gpt-6-luna` | `bytedance-seed/seedream-5-0-flash` | `google/veo-3.1-lite` | 1K / 720p |
| tests | `google/gemini-3.8-flash` | `google/gemini-3.1-flash-image` | `alibaba/wan-3.0` | 1K / 720p |
| production | `openai/gpt-6.1-sol` | `google/gemini-3-pro-image` | `google/veo-3.1` | 2K / 1080p |

Audio commun : `bytedance-seed/seed-audio-1-0`, 0,0025 $/s, non-speech,
120 s maximum par source, prompt de 3 000 caractères maximum.
Références image : maximum 14, hypothèse 3. Cadre technique provisoire : 16:9.
Préparation/production : clips **4/6/8 s**, tarifs vidéo respectifs 0,03 et 0,20 $/s.
Tests Wan : durées entières **2–30 s**, **6 s compatible**, 0,10 $/s à 720p,
première frame uniquement, pas de dernière frame ni de negative prompt.
Audio vidéo désactivé partout ; audio natif Wan sans tarif distinct connu et exclu.
Les autres résolutions supportées ne sont pas implicitement couvertes par ces prix.

## Fraîcheur, sources, incertitudes et exclusions

Snapshot config **2026-10-05**, âge **0 jour à la date de cette estimation**,
`current_snapshot`, limite configurée 30 jours. Sources déclarées OpenRouter :

- <https://openrouter.ai/api/v1/models>
- <https://openrouter.ai/api/v1/images/models>
- <https://openrouter.ai/api/v1/videos/models>
- <https://openrouter.ai/docs/guides/overview/multimodal/tts.md>

Ces sources sont celles de la config ; aucune actualisation réseau ou génération
de prix/qualité n'a été effectuée dans cette étape. Snapshot récent ne signifie
**ni devis, ni modèle testé, ni route/adaptateur/ComfyUI prêt à générer**.

Inconnus ou non inclus : tokens de raisonnement, texte/raisonnement interne aux
images, variation de tokenisation des références, contexte long, abonnement/coûts
réels du runtime LLM hérité, taxes/change et frais de crédits, licences/sources
existantes et éventuels coûts locaux de matériel/énergie, montage/mixage/finishing,
compositing des six surfaces, Foley, travail humain, stockage/transferts éventuels.
Ces coûts ne sont pas prouvés nuls. Les échecs peuvent rester facturables ; le cas
haut est une provision de reprises, pas une borne certaine du coût final.

**Musique facultative : exclue, coût inconnu, devis séparé si demandée**
(modèle/route, durée et licence à préciser) ; aucune musique hébergée ni Lyria
présumée gratuite. Les 60 s de sons ne comprennent aucune musique.

Le peu de lieux réduit les besoins de décors, mais ne garantit pas la facilité :
continuité de deux chats distincts (un seul animal actif par plan), adulte/enfant,
regards, mains/fruit/fumée, six projections et compositing restent délicats et
peuvent nécessiter davantage de reprises ou de travail local. Aucun niveau de
qualité/identité n'a été validé sur ce film.

## Revue à demander par la session principale

Recommandation de méthode seulement : rester en **préparation pour planifier**,
valider découpage, références et keyframes avant une éventuelle montée de gamme.
Ce n'est ni une sélection de gamme pour l'utilisateur, ni une commande de jobs.

La session principale doit présenter les trois alternatives et demander :
**quelle gamme et quel plafond USD souhaitez-vous retenir pour la planification,
et confirmez-vous explicitement la revue de cette estimation ?**
Ne pas créer `decision.yaml` sans réponse affirmative traçable. La décision devra
valider `schemas/budget-decision.schema.yaml`, lier ce SHA-256, la gamme et le
plafond réellement choisis, une référence de consentement non vide et le scope
`planning_only_not_spend_consent`. Toute modification des hypothèses/estimation
impose une nouvelle revue. Cette revue ne sera **jamais** un consentement aux jobs
payants : lots/modèles/paramètres/tentatives/coût/plafond exigeront un accord
supplémentaire explicite avant toute génération. Aucune installation, génération,
reprise automatique, étape screenplay ou approbation n'a été effectuée ici.

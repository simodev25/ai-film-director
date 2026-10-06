# La Pomme — réestimation après synchronisation artistique

**2026-10-05 — planification seulement, nouvelle revue nécessaire.**
Scope : `planning_only_not_spend_consent`. Aucun scénario, job, génération,
installation, backend/modèle runtime modifié ni approbation nouvelle.

## Baseline, changements et preuves conservées

Politique cloud, config des trois gammes et méthode relues ; compétences
`budget-estimation` et `cloud-production` chargées. Projet, histoire, hypothèses,
décision antérieure et brief artistique lus. La nouvelle histoire incorpore les
choix artistiques acquis : retour intérieur du travail en costume, refuge doux
et mélancolique, décor moderne vécu et lampe ambrée, apparences adulte/chats,
reflets puis écrans, enfance froide et banale, absence de paroles intelligibles.
Le souvenir du dessin et les autres points proposés ne sont pas approuvés par
extension. **L'ouverture est redistribuée dans les 420 s, sans nouvelle durée ni
augmentation automatique de jobs.** IDs conservés ; aucun artefact narratif
n'a été modifié par cette étape budgétaire.

- Story baseline de l'ancienne estimation :
  `1d6f8594dd21c23955ea82cce19ca2d9b204b32f280820e2160622573c2dfe4e`.
- Story actuelle vérifiée, liée à la nouvelle estimation :
  `bfd2b51651453fa33f5aeb586398ec002a33f19d009b535b843d8fe6a8f462d2`.
- Projet inchangé :
  `e04780e792e0cdecffc3b5b6d3e9e2726806e271747035db15ce5e1e977be29a`.
- Ancienne estimation revue :
  `afb4abb27306a20b7882ef6797ab890978dae2da37ff69ee192f6ca1f5b7abf6`.
- **Nouvelle estimation, SHA-256 des octets YAML sauvegardés** :
  `4a49770e662e28f4117c739201b67cec34d0b4a3a4873c8859699b24cedde770`.

Avant réexécution, copies exactes par patch Add File de estimate.yaml/md,
decision.yaml, review-consent.md, review-notes.md et assumptions.yaml dans
[`history/review-01/`](history/review-01/). Identité des octets vérifiée avant
écrasement CLI ; empreintes consignées dans archive-notes.md. Les fichiers actuels
decision.yaml, review-consent.md, review-notes.md et assumptions.yaml restent
**inchangés**. Les anciens rapports/accords décrivent leur état historique.

Commande réelle exécutée après contrôle de son aide :

```sh
PYTHONPATH=src /usr/local/bin/python3 -m cli budget projects/la-pomme \
  --assumptions projects/la-pomme/budget/assumptions.yaml
```

Le YAML est exclusivement celui produit par cette CLI ; seul le Markdown reçoit
un lien vers ce complément. Validation via les schémas projet, story,
budget-assumptions, budget-estimate et budget-decision : **réussie**.
La décision est valide **syntaxiquement**, mais son ancien estimate_sha256 ne
correspond plus : elle est stale, pas renouvelée. État vérifié après recalcul :

```yaml
estimated: true
reviewed: false
reason: estimate_changed
```

## Hypothèses communes maintenues

- **420 s, 70 futurs clips de 6 s** proposés, aucun shot ID créé. Peu de lieux
  limite les décors mais pas le nombre de renders : environ 70 vidéos, pas
  quelques longs plans. Continuité adulte/enfant, deux chats distincts (un seul
  actif), costume, regards, fumée, fruit et six projections restent difficiles.
- **82 images = 70 keyframes + provision de 12 illustrations modèles/références**.
  Les 12 sont des outputs futurs, pas des entités ou IDs actifs. Même provision
  conservatrice malgré les références externes approuvées ; quantité à revoir
  après fiches, vues complémentaires et découpage, pas à réduire implicitement.
- **3 inputs référence par image** en moyenne forfaitaire, 246 usages par passe,
  pas 246 images générées. Charge input incluse : 0 / 0,137760 / 0,275520 USD
  respectivement. Input référence préparation sans supplément, output payant.
- Vidéo 420 s par passe, fraction 1, **audio natif désactivé** partout.
- **60 s Seed Audio de sons isolés non verbaux ; 0 s de parole/TTS**, sans
  narration. Sources à réutiliser et composer en couches locales/procédurales,
  pas 420 s de bande-son générée. Schéma sans distinction parole/sons : précision
  en prose. Suppression future des jobs Seed implique `audio_seconds: 0`,
  réestimation puis nouvelle revue.
- **100 000 tokens input / 20 000 output** théoriques, contexte standard
  <272 000 tokens par appel. Recommandations config, pas coûts observés du LLM
  OpenCode hérité. Raisonnement inconnu/exclu, aucune bascule de runtime.
- Multiplicateurs **1 / 1,25 / 1,75**, reprises **0 / 25 / 75 %**, appliqués à
  tous les postes ; **réserve supplémentaire 10 %** après reprises. Ni moyenne
  empirique, ni garantie, ni permission de retry ; les échecs peuvent être payants.
- **Musique facultative exclue, coût UNKNOWN, devis séparé si demandée**.

## Comparaison et deltas exacts — USD

| Gamme | Images / vidéo | Bas | Moyen | Haut | Delta bas / moyen / haut |
|---|---|---:|---:|---:|---|
| préparation — choix antérieur utilisateur | 1K / 720p | 15,670600 | 19,588250 | 27,423550 | 0 / 0 / 0 |
| tests — comparaison seulement | 1K / 720p | 52,742976 | 65,928720 | 92,300208 | 0 / 0 / 0 |
| production — comparaison seulement | 2K / 1080p | 105,430952 | 131,788690 | 184,504166 | 0 / 0 / 0 |

Hypothèses et résultats `tiers` identiques à l'archive, comparaison vérifiée.
Seuls l'horodatage et le lien à la story changent dans le YAML. Les coûts
inchangés ne rendent pas le consentement valable pour un nouvel estimate_sha256.
Trois alternatives du même film, pas trois séries à produire ni budget cumulé.

Première passe avant reprises/réserve, ventilation conservée :

| Poste | Préparation | Tests | Production |
|---|---:|---:|---:|
| Texte théorique | 0,020000 | 0,150000 | 0,400000 |
| 70 keyframes, inputs inclus | 1,260000 | 4,821600 | 9,643200 |
| 12 illustrations provisionnelles, inputs inclus | 0,216000 | 0,826560 | 1,653120 |
| Vidéo 420 s | 12,600000 | 42,000000 | 84,000000 |
| Sons isolés 60 s | 0,150000 | 0,150000 | 0,150000 |
| Sous-total | 14,246000 | 47,948160 | 95,846320 |

Total = sous-total × multiplicateur × 1,10. Le CLI affiche quatre décimales ;
ce tableau conserve les valeurs YAML à six décimales, sans prétendre à cette
précision contractuelle. La réserve n'est pas le plafond choisi.

### Clips, modèles et réglages

La CLI n'accepte pas de nombre de shots ni de durée commune de clip dans les
hypothèses : ses **53 / 14 / 53 clips** sont des agrégats aux durées maximales
(52 × 8 + 4 s pour Veo ; 14 × 30 s pour Wan), pas les futurs plans. La proposition
70 × 6 s respecte toutes les caps et donne aussi 420 s sans arrondi supplémentaire,
donc mêmes prix à la seconde. Revoir minima par appel, raccords et vrais shots
ultérieurement ; ne pas modifier le YAML pour prétendre que la CLI compte 70 jobs.

| Gamme | Texte recommandé | Image | Vidéo |
|---|---|---|---|
| préparation | openai/gpt-6-luna | bytedance-seed/seedream-5-0-flash | google/veo-3.1-lite |
| tests | google/gemini-3.8-flash | google/gemini-3.1-flash-image | alibaba/wan-3.0 |
| production | openai/gpt-6.1-sol | google/gemini-3-pro-image | google/veo-3.1 |

Audio commun : bytedance-seed/seed-audio-1-0, 0,0025 USD/s, non-speech,
maximum 120 s/source, prompt maximum 3 000 caractères. Image : jusqu'à 14
références, hypothèse 3. Vidéo préparation/production : **4/6/8 s**, 0,03 / 0,20
USD/s aux résolutions indiquées ; tests Wan : **2–30 s entières**, 6 s compatible,
0,10 USD/s à 720p, première frame uniquement, sans dernière frame ni negative
prompt. Cadre provisoire 16:9. Pas d'upgrade ni d'audio natif Wan non tarifé.

## Références externes : approbation créative ≠ preuve de coût/qualité cloud

Le brief artistique consigne l'accord utilisateur sur adulte, décor et deux chats,
mais les essais annoncés comme GPT ont modèle exact, version et coût **UNKNOWN**.
Ils sont distincts du budget prospectif du film cloud et ne sont pas déclarés
gratuits. Aucun coût historique de ces essais n'est soustrait, ajouté comme connu,
ni utilisé comme facture du modèle image préparation.

Des PNG sont présents dans `art-direction/` au contrôle de répertoire ; leur
présence ne prouve pas un import/registre de production validé, un mapping canonique,
des crops appropriés, des turnarounds ou des fiches multi-vues utilisables. Cette
étape ne les importe pas, ne les examine pas et ne les compte pas automatiquement
comme remplacement des 12 illustrations. Le brief les décrit encore comme essais
externes approuvés créativement ; toute évolution d'import devra être vérifiée à
l'étape dédiée avant de réestimer. **Un accord visuel externe GPT ne valide ni la
fidélité Seedream, ni son coût exact, ni la disponibilité d'un workflow.**

## Tarifs, exclusions et revue à renouveler

Snapshot config **2026-10-05**, âge **0 jour** à cette réestimation ;
`current_snapshot`, limite 30 jours. Sources OpenRouter déclarées :

- https://openrouter.ai/api/v1/models
- https://openrouter.ai/api/v1/images/models
- https://openrouter.ai/api/v1/videos/models
- https://openrouter.ai/docs/guides/overview/multimodal/tts.md

Pas de vérification réseau ou génération tarifaire. Pas un devis, facture,
benchmark de qualité ni preuve de readiness. Images/références Google : tarifs
estimés par tokenisation, non forfaits contractuels garantis. Exclus/inconnus :
raisonnement, texte/raisonnement image, tokenisation effective, contexte long,
abonnement/runtime LLM hérité, frais/taxes/change, licences, essais externes,
coûts locaux/énergie/stockage/transferts, Foley, compositing des surfaces,
montage/mixage/finishing et travail humain. Inconnu ≠ zéro. Haut ≠ borne certaine.

L'utilisateur avait retenu **préparation, cas bas, plafond 30 USD** sur l'ancienne
estimation ; tests et production ne sont pas choisis. La session principale doit
demander la **reconfirmation explicite** de ce choix pour le **nouveau hash**,
sans présumer l'accord au motif que le coût reste 15,670600 USD. Aucun nouveau
consentement n'est enregistré ici, et decision.yaml actuel demeure inchangé.
Sans revue correspondante, pas de passage au screenplay. Une éventuelle décision
renouvelée doit lier hash, gamme, plafond et référence d'accord traçable ; elle
reste planning_only_not_spend_consent, jamais consentement de génération.

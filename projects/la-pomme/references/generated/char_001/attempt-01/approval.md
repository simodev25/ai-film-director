# `char_001` adulte — preuve d'approbation limitée et crops locaux

Date : **2026-10-05**. Session source : `ses_ef27d5cdcffefU62W3ufHMHm2L`.
Preuve transmise par la session principale, sans message ID inventé.

**Question exacte :** « Tu valides son apparence et sa tenue, chaussures
comprises ? Le profil reste à corriger ; cette validation n’autorisera pas
automatiquement une nouvelle génération. »

**Réponse exacte : « oui go ».**

## Ce qui est approuvé et ce qui ne l'est pas

- Apparence adulte visible et silhouette de `char_001` dans la tentative 01,
  visage/coiffure/barbe et tenue : costume anthracite, chemise gris clair col
  ouvert sans cravate, pantalon, chaussures de ville noires mates comprises.
- Les chaussures et complétions visibles ne sont donc plus de simples propositions
  dans le périmètre de cette sortie ; aucune mensuration exacte, ethnie, couleur
  précise des yeux ou apparence enfant n'est ajoutée.
- **Non approuvé :** conformité stricte de tous les angles. La troisième figure
  reste trop proche du trois-quarts ; un profil corporel réel manque.
- **Non autorisé :** nouvelle génération payante ou retry. « Go » demande de
  préparer la correction ; aucun nouveau coût n'a été cité dans cette question.
  Le précédent consentement à une tentative payante est distinct et épuisé par
  la tentative 01. Le stade canonique personnages n'est pas déclaré complet.

## Parent conservé intégralement

Chemin relatif à `projects/la-pomme` :
`references/generated/char_001/attempt-01/fbe7c67f_000.png`.

Dimensions **1280 × 720** ; SHA-256 vérifié avant et après les crops :
`06d3c347e907508d69885257b08d222c465525bdacea7a993052077a3d6ea4dd`.

Provenance de ce parent seulement : `bytedance-seed/seedream-5-0-flash`,
`preparation`, paramètre 1K 16:9, une tentative ; job
`fbe7c67f-895e-4333-8181-ce1967d46d49`. Coût réel transmis par le record de la
session principale : **0,018 USD**. Le portrait GPT externe initial reste une
autre provenance, modèle/version/coût inconnus ; aucune attribution Seedream
globale au registre et aucun coût externe supposé nul.

## Trois dérivés locaux, pas trois nouvelles illustrations

Crops créés avec le **Pillow déjà installé**, sans install, appel modèle, retouche,
resize, harmonisation ou génération. Coût additionnel de génération : aucun.
Chaque crop de **320 × 720** a été réellement relu : cheveux, corps entier,
chaussures et marge conservés, sans figure adjacente coupée dans le champ.
Les boxes sont en pixels du parent : `[left, top, right, bottom]`, bornes
right/bottom exclusives, convention Pillow. Toutes les lignes ci-dessous sont
enregistrées dans `views` de l'entrée parent **ordre 4** du registre.

| Vue | Chemin relatif au projet | Box | SHA-256 |
| --- | --- | --- | --- |
| Front | `references/generated/char_001/attempt-01/crops/front.png` | `[0, 0, 320, 720]` | `b476d09210ae02681be1fa35eb67de44350ff031697e2cf4fe5cf3549435c4a2` |
| Left 3/4 (`three_quarter`) | `references/generated/char_001/attempt-01/crops/left-three-quarter.png` | `[320, 0, 640, 720]` | `9269ab7400fb3d073bfdaf3ade5be30b92efeb25279fd1fa709f70cd3d51e0ba` |
| Back | `references/generated/char_001/attempt-01/crops/back.png` | `[960, 0, 1280, 720]` | `0d63ae9fdc4080e2f9efa9cff1394fd2495b7b227b7c4031da515c85a2b65e4e` |

Ces fichiers sont **dérivés de l'apparence du parent approuvée**, sans accord
artistique autonome prétendu. Aucun crop du troisième panneau ni `view: profile`
créé : ne pas rendre le profil non conforme sûr par un simple label.

## Suite préparatoire seulement

Draft séparé : `references/drafts/char_001-profile-correction.prompt.yaml` ;
plan : `references/drafts/profile-correction-plan.md`. Un seul profil isolé
plein corps envisagé, puis revue utilisateur avant toute composition locale
éventuelle. Les trois figures originales ne seront pas régénérées et le parent
ne sera pas écrasé. Pas de nouvelle autorisation payante, graphe/ledger, budget,
story, projet ou stade créatif avancé ici.

## Vérifications locales effectuées

YAML parsés ; ordre 1–4, champs/enums requis du schéma réel
`schemas/approved-references.schema.yaml`, types, contraintes de hash, boxes et
dates contrôlés par un vérificateur local couvrant les contraintes utilisées par
ce schéma. La bibliothèque `jsonschema` n'est pas disponible dans le Python
utilisé ; aucune installation ni validation par cette bibliothèque revendiquée.
Tous les hashes des sources/parent/crops correspondent aux fichiers ; les trois
crops correspondent pixel pour pixel aux boxes du parent. Draft du profil :
chaîne `prompt`, une référence, 1K 9:16, une image/une tentative, sans override de
seed et coût réel null contrôlés. Aucun cloud-job ou workflow validé ici.

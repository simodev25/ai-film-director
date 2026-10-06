# Deux chats — préparation de deux planches dans un seul batch futur

## Demande réelle et arrêt avant dépense

Demande transmise de la session principale : **« go fait les 2 en meme temps »**.
Préparer les deux chats ensemble est acquis ; la session principale a annoncé
préparer leurs deux planches dans le même style avant la demande de coût total.
**Aucun consentement chiffré au nouveau batch n'est encore donné.** Ce dossier
n'autorise aucune génération, upload, réserve/claim/ledger, installation ou retry.
Pas de batch/scaffold créé par ce sous-agent, ni étape canonique personnages avancée.

Les IDs existants restent **`char_002` = tigré gris-brun** (motif de pelage, pas
race inventée), **`char_003` = Persan crème** ; `project_la_pomme` inchangé. Pas de
nom, sexe, taille, âge précis, mensuration ou couleur numérique des yeux inventés.

## Sources effectivement examinées et ordonnées

La source chats approuvée entière, réellement lue, est
`art-direction/Salon chaleureux, chats sous les lumières nocturnes.png`,
**1672 × 941** ; hash
`89015ce187d726d5560edc92d4f8f20d4f08d1406117ad2e8963a5199254b5a8`.
Elle garde ses deux liens d'entités aux ordres 2/3, sa provenance GPT externe
modèle/version/coût inconnus et ses approbations initiales. Aucun nouvel accord
de planche future prétendu. Les crops locaux sont détaillés dans
`references/source-crops/cats/derivation.md` et `derivation.json`.

| Draft / ID stable | Référence 1 : identité du chat | Référence 2 : style seulement |
| --- | --- | --- |
| `char_002-turnaround.prompt.yaml` / `ref_char_002_turnaround_01` | `references/source-crops/cats/char_002-source-conditioning.png` | `art-direction/Homme fatigué dans un appartement nocturne.png` |
| `char_003-turnaround.prompt.yaml` / `ref_char_003_turnaround_01` | `references/source-crops/cats/char_003-source-crop.png` | Même portrait adulte approuvé |

Chemins relatifs à `projects/la-pomme`. **Exactement deux images de conditioning
par futur job**, dans cet ordre. Le portrait adulte, réellement relu, est lié à
`char_001`, hash
`7e85faaddab814f55012065755fc28d2651891567b642ad11053551d9aee1314` ; il sert
**uniquement au graphisme**, jamais à représenter l'homme, sa tenue, son visage
sur le chat ou son décor/lumière nocturne. Pas de feuille adulte multi-vues utilisée.

**Isolation du tigré :** crop brut 600 × 495 conservé, puis fichier conditioning
distinct à masque gris `[0,0,240,55]` sur le seul fragment de Persan/décor dans son
coin haut gauche. Ce n'est pas une pure crop. Corps/oreilles/pattes/queue du tigré
ne sont pas dans le masque selon lecture visuelle ; tous les pixels hors masque
restent identiques. Aucune retouche du chat ou harmonisation réalisée. Le crop
Persan 450 × 217 est pur, sans tigré ; ses parties cachées restent inconnues.
Du mobilier reste visible dans les crops : les prompts prescrivent de l'ignorer.

## Une image par animal, six vues dans chaque image

**Trois colonnes × deux lignes**, sans texte, labels ni lignes de séparation :

| Ligne | Colonne 1 | Colonne 2 | Colonne 3 |
| --- | --- | --- | --- |
| Haut | Debout face | Debout gauche 3/4 | Debout vrai profil gauche |
| Bas | Debout dos | Assis gauche 3/4 | Couché gauche 3/4 |

Même individu répété six fois, échelle corporelle constante entre les vues ;
assis/couché ne sont pas agrandis artificiellement pour remplir les cellules.
Profil de **tout le corps**, pas tête tournée sur torse trois-quarts. Anatomie
féline naturelle à quatre membres, occlusions normales admises, oreilles/pattes/
queues complètes dans les cellules avec marge ; aucun autre chat/humain ou
accessoire, anthropomorphisme, chibi, photo, 3D plastique, décor ou floor plan.

- **Tigré :** poil court gris-brun, marques faciales/rayures visibles, oreilles,
  moustaches, museau plus clair, jambes rayées et queue annelée visibles conservés.
  Pas de nouveau compte précis de rayures/anneaux ou d'yeux recolorés.
- **Persan :** crème, poil long épais, volume et collerette distincts, face ronde
  et museau court/aplati **tels qu'ils apparaissent**, oreilles/moustaches/queue
  touffue conservées, sans hypertype nasal ajouté ou transformation en tigré.
- **Graphisme commun :** contours fins visibles et ombres cel painterly du
  portrait adulte, légère simplification future des poils/ombres déjà autorisée
  créativement, silhouettes/anatomie et marques préservées. Fond gris neutre,
  lumière diffuse identique dans la planche, teintes lisibles et influence olive/
  charbon discrète, pas recopie des rim lights ambre ou du salon.

Faces/poils/anatomie non vus, nouveaux angles et poses sont des **complétions
proposées à revoir**, pas de nouveaux faits approuvés. Même la bonne intention
stylistique ne démontre pas sa réalisation ou la fidélité de Seedream.

## Paramètres et coût préparatoire, pas accord

Les deux YAML portent une chaîne top-level **`prompt`**, dotted key **`prompt`**
à consommer après adaptation par la session principale. Les IDs de prompt sont
ceux du tableau ; aucun `shot_id`/`scene_id` ou nouvelle entité fictive.

| Paramètre | Par chat | Total du batch envisagé |
| --- | --- | --- |
| Gamme / modèle unique | `preparation` / `bytedance-seed/seedream-5-0-flash` | Identiques sur les deux jobs |
| Résolution / format | **1K / 16:9**, pas d'override seed | Aucun upgrade/fallback |
| Images / tentatives | **1 image / 1 tentative** | **2 illustrations, 2 tentatives au total**, pas 12 appels |
| Références | **2** ordonnées, identité puis style | 2 par job, sous le cap 14 |
| Estimation configurée | **0,018 USD**, références 0,000 USD selon le profil | **0,036 USD** |
| Plafond proposé NON approuvé | **0,020 USD** | **0,040 USD** |
| Coût réel futur | **Inconnu / null** | Inconnu, aucun job lancé |

Tarifs de `config/cloud-tiers.yaml`, vérifiés dans la configuration au
**2026-10-05**, pas facture future ni generation-call de test prix. Compte distinct
des shots : **2 images de référence animaux, 0 render de shot**. Crops locaux
ne sont pas des images générées supplémentaires. Aucune modification de budget
pour inférer une autorisation ; la session principale vérifiera revue, plafond
restant et tarification route spécifique avant la demande payante.

## Suite réservée à la session principale

Adapter deux jobs/scaffolds à **deux références réellement chargées et ordonnées**,
vérifier descripteurs live, options du modèle, bindings, 1K 16:9 et graphe exact
sur la cible. Les drafts ne sont pas des cloud-jobs validés ni des prompts de shot
faussement schema-valides ; `schemas/cloud-job.schema.yaml` fera autorité après
adaptation. Aucune vérification live, upload ou installation effectués ici.

Puis présenter **une seule demande de consentement chiffrée pour les deux jobs**,
leur liste, modèle, références, paramètres, une tentative chacun, coût/plafond
total ; seulement après la réponse explicite traiter approvals/ledger/submission
dans la session principale. Aucun retry ou autre modèle implicitement autorisé.
Après génération : revue des deux planches puis user approval, avant inscription
des sorties approuvées et crops de vues. Le présent registre n'ajoute que les
dérivés des apparences sources déjà approuvées, pas des sorties encore inexistantes.

Gardes lues : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`, `docs/film-method.md`,
skills `model-sheets` / `cloud-production` et schéma réel du registre. Aucun
personnage canonique, story, projet, budget, stage, audio ou prompt d'autre modèle
créé ou modifié dans cette préparation.

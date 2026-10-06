# La Pomme — import des références acquises et vues futures

Date : 2026-10-05. **Import/registre seulement ; aucun rendu ni fiche canonique.**

Priorité utilisateur transmise par la session principale : « on dois fixer les
personer pour le remais comme refrenece », avant le storyboard de scène 1.
L'import des sources déjà approuvées peut être documenté maintenant ; il ne
prétend pas avoir réalisé les étapes screenplay → personnages/fiches → art
direction détaillée → model sheets → storyboard. Revue budgétaire actuelle et
screenplay requis avant l'avancement des fiches canoniques. Aucun fichier de
story, projet ou budget n'est modifié par ce travail.

## Sources locales et ordre des références

Les chemins suivants sont **relatifs à `projects/la-pomme/`**, pas à la racine
du dépôt. Les trois PNG originaux restent en place, sans renommage, copie,
modification ou découpe. Les noms à accents sont conservés exactement.

| Ordre registre | Entité existante | Source | Statut / limites |
|---|---|---|---|
| 1 | `char_001`, variante adulte | `art-direction/Homme fatigué dans un appartement nocturne.png` | Portrait complet approuvé pour visage/coiffure/barbe/costume ; pas une fiche multi-vues. |
| 2 | `char_002`, tigré gris-brun | `art-direction/Salon chaleureux, chats sous les lumières nocturnes.png` | Apparence visible approuvée ; source commune avec le Persan, non isolée. |
| 3 | `char_003`, Persan crème | Même PNG des deux chats | Apparence visible approuvée ; source commune avec le tigré, non isolée. |

Ces **3 liens d'entités représentent 2 fichiers uniques**, pas trois rendus ni
trois nouvelles illustrations. Le registre conserve cet ordre ; une future
liste de fichiers soumise au modèle distinguera ordre d'entités et déduplication
technique du PNG commun, sans intervertir les identités. Les crops isolés futurs
permettront une référence distincte par chat. Les sources ne sont ni des grilles
ni des keyframes. Aucun `sheet_type` ou vue non observée n'est attribué au registre.

Preuves : les questions exactes et réponses **« oui »** de la session principale
`ses_ef27d5cdcffefU62W3ufHMHm2L` sont reprises par entrée du registre et conservées
dans `art-direction/style-brief.md`. Elles fixent l'apparence adulte et les
apparences des chats avec harmonisation légère **acceptée mais non réalisée**.
La provenance annoncée est un essai externe GPT ; modèle exact, version et coût
restent **inconnus**, jamais Seedream par attribution rétroactive, jamais zéro.
L'enregistrement utilise les octets locaux et leurs SHA-256 réels.

### Source décor disponible, sans ID de lieu inventé

`art-direction/Unknown.png` est l'aperçu horizontal du salon approuvé pour
**disposition, mobilier et lumière**, pas pour l'homme, le contenu TV ou un plan
définitif. SHA-256 :

```text
e7f162790e20fa4079a1f638eb6c87495834c5254869f0ef7f5df885d42c3d7f
```

Question exacte : « Tu valides cette image comme référence du salon — disposition,
mobilier et lumière compris ? Ce sera référence décor pas plan définitif film. »
Réponse **« oui »**, même session source, enregistrée le 2026-10-05. Le fichier
est disponible, mais **aucun ID canonique de lieu n'existe encore** : aucune
entrée `location` artificielle ajoutée. Il sera rattaché au véritable ID lors de
l'étape lieux. Cette mention n'approuve ni géométrie cachée ni droits du contenu
TV (à recréer en fiction originale).

## Plan de vues futur — sans jobs préparés ou autorisés

Conserver `char_001`, `char_002`, `char_003` dans toutes les scènes. L'enfant est
une époque de `char_001`, jamais un nouvel ID. `char_004` et `char_005` restent
parents hors champ : pas de portraits inventés. Aucun nom, nouvelle personnalité
ou voix parlée n'est fixé ici ; film sans paroles intelligibles et sans TTS.
Les futurs anchors d'identité/voix réutilisables seront portés par les fiches
canoniques après screenplay, sans modifier les choix déjà acquis.

| Entité | Feuilles à prévoir | Vues et contrôles |
|---|---|---|
| `char_001` adulte | 1 turnaround, 1 expression sheet, 1 feuille de la tenue adulte approuvée | Turnaround : face, trois-quarts, profil, dos, **corps entier**, pose neutre ; proportions, visage, coiffure, barbe stables. Expressions proposées : neutre, fatigue, retenue, vulnérabilité — à valider, pas poses narratives acquises. Tenue : costume anthracite/chemise gris clair col ouvert sans cravate ; compléter les détails hors champ, **pantalon/chaussures non fixés par le portrait**. Pas de variante veste retirée présumée. |
| `char_002` | 1 turnaround animal incluant assis/couché, 1 expression sheet | Face, trois-quarts, profil, dos + assis + couché : **une image grille par turnaround** avec six cases explicitement définies. Isoler ce chat, conserver gris-brun/rayures/silhouette ; harmonisation légère poils/ombres vers le portrait. Expressions naturelles proposées, non anthropomorphiques ; aucun costume. |
| `char_003` | 1 turnaround animal incluant assis/couché, 1 expression sheet | Même ensemble de six vues/poses, **une image grille par turnaround**, indépendamment de char_002. Crème, poil long/volume du Persan, silhouette et visage visibles conservés ; harmonisation légère sans changer la race ou inventer des détails cachés. Aucun costume. |

Soit **7 feuilles/images futures indicatives** pour ces trois apparences, environ
une image par feuille, sans les compter comme rendus de shots. Ce n'est ni un lot
final ni une modification de l'estimation : le budget-agent gère la provision et
la revue globale. L'enfant nécessitera ses propres turnaround/expression/tenue
par époque **après définition et approbation de son apparence** ; quantité encore
ouverte. Tout ajout de tenue/ère implique sa propre feuille et sa revue. Le salon
nécessitera 3–4 angles et un plan au sol (fenêtres, TV, portes, mobilier) après
création de son ID ; pas de localisation ou géométrie hors champ inventée.

Les futures feuilles : fond uni, lumière neutre régulière, vues complètes non
occluses, nombre et layout explicites, **aucun texte dans l'image**. Les sources
actuelles n'apportent pas de nouvelles vues : un crop ne peut créer profil ou dos.
Une découpe locale éventuelle isolera seulement l'apparence réellement visible,
avec label prudent `other` si l'angle n'est pas assuré. Elle ne sera pas qualifiée
de nouvelle harmonisation ni de nouveau graphisme revu par l'utilisateur.

## Approbation, crops et utilisation ultérieure

1. Vérifier la revue budgétaire liée à l'estimation actuelle, puis réaliser
   screenplay et fiches canoniques dans l'ordre de `docs/film-method.md`.
2. Si les illustrations sont explicitement demandées, utiliser **un seul modèle
   image de la gamme effectivement sélectionnée**. L'orientation de préparation
   actuelle est `bytedance-seed/seedream-5-0-flash` (1K par défaut), pas une source
   de ces PNG ni une preuve de disponibilité/fidélité. Pas de fallback legacy.
3. Préparer/valider la route réelle, effectuer le scan des options requis, revoir
   le budget des **illustrations liées aux entités, séparé des images de plans**.
   Présenter une liste de jobs `reference_illustration`, paramètres, références
   ordonnées, tentatives, total et plafond ; demander un **accord payant explicite
   pour ce lot** via la session principale. Les « oui » d'apparence ne le donnent pas.
4. Après génération autorisée, présenter chaque feuille à l'utilisateur. Ne
   l'enregistrer comme feuille approuvée qu'après son accord ; correction ou
   tentative supplémentaire = nouvel accord si hors du lot accepté.
5. Garder la feuille entière puis découper chaque vue isolée localement (sans
   modèle) ; enregistrer `views[].view`, `asset_path`, `sha256`, `box` et `label`
   selon le schéma. L'entrée parent porte `path`/`sha256` et `sheet_type` ; ne pas
   inventer un champ parent absent du schéma. Assis/couché/expressions utiliseront
   `view: other` avec label explicite. Vérifier les crops et leur cadrage.
6. Pour les shots, fournir la **vue isolée correspondant à l'angle**, pas la
   grille entière ni une source à deux chats pour feindre une identité isolée ;
   déclarer `reference_entity_ids` et la vue utilisée, conserver les anchors.
   Un seul chat actif à la fois ; positions initiales non permanentes.

## Contrôle de cette importation

Registre : `references/approved-references.yaml`, schéma
`schemas/approved-references.schema.yaml`. Contrôles : `project_id` réel,
ordres `[1, 2, 3]`, IDs présents dans la story, chemins locaux et SHA-256 des PNG.
Ce Markdown est un plan libre, pas une fiche YAML validée contre les schémas
personnage. Aucun crop, nouvelle image, prompt exécutable, batch, upload, scan
ComfyUI ou génération effectué. Les PNG sont inchangés.

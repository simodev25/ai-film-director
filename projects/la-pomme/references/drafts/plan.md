# `char_001` adulte — premier turnaround exploratoire

## Périmètre : planning seulement

Une **seule image de référence exploratoire**, liée à l'identité existante
`char_001` du projet `project_la_pomme`. Elle contient quatre vues en une rangée :
**FRONT → LEFT 3/4 → LEFT PROFILE → BACK**. « Left » désigne le côté gauche
anatomique visible ; dans les vues gauche 3/4 et profil, le nez pointe vers la
gauche de l'image. Ce sont des consignes de composition, pas des labels à rendre.
Il ne s'agit ni de quatre appels, ni d'un shot, ni d'une nouvelle entité canonique.

Le choix transmis de passer ultérieurement par le projet puis de poursuivre
uniquement l'adaptation technique ne constitue pas une autorisation de dépense.
Aucun appel ComfyUI, job, workflow, consentement, crop ou média créé ici. Aucun
screenplay, fichier de personnages/fiches canoniques ou stade créatif avancé.
Seuls ce plan et le draft YAML associé sont écrits.

## Source examinée et ancrages conservés

- Fichier réellement lu :
  `projects/la-pomme/art-direction/Homme fatigué dans un appartement nocturne.png`.
- SHA-256 vérifié :
  `7e85faaddab814f55012065755fc28d2651891567b642ad11053551d9aee1314`.
- Référence ordonnée **1**, seule entrée utilisée pour ce draft : portrait adulte
  déjà lié à `char_001` dans `references/approved-references.yaml`. Son chemin
  dans le YAML est relatif à `projects/la-pomme`, comme dans le registre.
- Brief réellement lu : `projects/la-pomme/art-direction/style-brief.md`, avec
  sa mise à jour d'import local en tête ; les mentions historiques de fichier
  absent ne décrivent plus l'état actuel.
- Visage anguleux, cernes et fatigue, cheveux bruns foncés courts désordonnés à
  mèches, barbe courte : **identité adulte conservée**, sans embellissement.
- Costume anthracite, chemise gris clair à col ouvert, sans cravate : tenue
  retenue ; aucune chemise ivoire, nouveau costume vert, trench ou accessoire Matrix.
- Trait semi-anime à proportions réalistes, contours sombres fins visibles,
  ombres cel painterly en facettes : maintenir ce langage dessiné, sans photo,
  chibi ou 3D plastique. Influence Matrix olive/charbon discrète dans le graphisme,
  pas reproduction du décor ou de la lumière nocturne du portrait.
- Aucun âge exact, taille métrique, ethnie ou couleur précise des yeux inférés.
  La variante enfant reste hors périmètre et conserve la même identité `char_001`.
  Aucun nouvel ancrage vocal ou TTS : les choix existants sans paroles intelligibles
  restent intacts.

## Propositions visuelles nouvelles — non approuvées

1. **Chaussures de ville simples noires mates** : hors champ dans la source,
   donc proposition de complétion et non apparence déjà approuvée.
2. Bas des jambes/pantalon, coupe complète et dos du costume prolongeant
   sobrement l'anthracite visible ; détails cachés et proportions complètes
   restent des hypothèses exploratoires, pas des mensurations canoniques.
3. Arrière de la tête/du corps, poses neutres debout, mains visibles et vides :
   nouvelles vues de comparaison. Ne pas figer comme posture permanente la pose
   appuyée dans l'entrée, la main dans la poche ou le regard baissé de la source.
4. Fond gris neutre uni, lumière douce diffuse uniforme : adaptation lisible
   pour comparer les vues, pas nouvelle lumière approuvée pour le film.

Tous ces éléments demanderaient une revue de l'image éventuelle. Le portrait
approuvé n'approuve pas à l'avance le turnaround ni ses complétions.

## Prompt et paramètres futurs

Artefact : `references/drafts/char_001-turnaround.prompt.yaml`.
**Clé du prompt : `prompt`**, chaîne top-level, utilisable comme dotted key
`prompt` par l'adaptation ultérieure. Le YAML reste un draft documentaire :
aucune validation fictive contre le schéma de prompts de shots, aucun
`scene_id` ou `shot_id` inventé. Après adaptation, le plan d'exécution devra
être contrôlé contre `schemas/cloud-job.schema.yaml` et le graphe exact contre
le ComfyUI cible. Ce texte n'est ni ce plan validé ni une preuve de disponibilité.

| Paramètre | Valeur planifiée | Limite / coût |
| --- | --- | --- |
| Gamme | `preparation` | Un seul modèle image, aucun fallback |
| Modèle exact | `bytedance-seed/seedream-5-0-flash` | Résolution live à vérifier par la session principale |
| Route future | `comfyui_project_adapter_via_comfy_mcp` | Pas d'appel direct fournisseur |
| Résolution | **1K** | Aucun upgrade 2K silencieux |
| Format | **16:9** | Quatre corps entiers dans une seule image |
| Images / tentative | **1 image / 1 tentative** | Aucun retry autorisé ici |
| Références | **1**, portrait adulte en ordre 1 | Aucune référence de salon ou de chats |
| Seed | **Non explicitement fixé** | Pas de valeur ajoutée au draft |
| Estimation configurée | **0,018 USD** pour la sortie | Référence : 0,000 USD selon le profil configuré ; sortie payante |
| Coût réel | **Inconnu / null** | Aucun job, aucune facture observée |

Tarif issu de `config/cloud-tiers.yaml`, vérifié dans la configuration le
**2026-10-05**, pas un devis live ni un coût effectivement payé. Cette image
compte séparément comme **1 illustration de référence, 0 render de shot**.
Aucun budget ou plafond n'est créé ou modifié ici ; la session principale
contrôle la revue budgétaire et l'intégration de ce compte avant toute dépense.

## Suite réservée à la session principale

L'adaptation technique devra inspecter les capacités réelles du projet, le
descripteur live du modèle et ses options, les bindings et l'ordre de référence,
sans générer. Résolution, format, quantité de sortie et éventuels paramètres
qualitatifs doivent rester ceux de ce plan ; incompatibilité = blocage déclaré,
pas substitution ou upgrade. Aucun descripteur live ni readiness n'est attesté ici.

Avant un éventuel job payant : budget revu valide, prix route-spécifique courant,
plan et graphe exacts validés, consentement explicite de job/batch couvrant modèle,
paramètres, référence, **une tentative** et coût/plafond, puis réservation ledger.
L'accord de planning ou l'approbation du portrait ne remplace pas ces gardes.
La session principale gère le scaffold/catalogue et tous les autres artifacts.

Après génération seulement, présenter l'image à l'utilisateur et contrôler
l'identité, les quatre angles, les corps entiers, la palette des vêtements et la
lisibilité uniforme. Ne pas inscrire d'approbation par avance. Si l'utilisateur
approuve ensuite cette image, la conserver entière et réaliser localement les
quatre crops isolés, puis les enregistrer selon les champs réellement supportés
du registre avec leurs hashes et leur parent ; aucun crop ou enregistrement ici.
Les expressions et autres tenues/époques prévues par `model-sheets` ne sont pas
incluses dans cette première exploration et ne déclenchent aucun appel additionnel.

Sources de méthode lues : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`,
`docs/film-method.md`, skills `character-design`, `model-sheets`, `cloud-production`,
schémas character/character-sheet, story et registre existants. Ces schémas
canoniques ne sont pas appliqués abusivement à ce draft exploratoire.

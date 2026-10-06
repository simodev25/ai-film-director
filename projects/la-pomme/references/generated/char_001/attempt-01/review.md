# `char_001` adulte — revue visuelle de la tentative 01

**Statut courant au 2026-10-05 : apparence/tenue/chaussures approuvées ; profil
strict toujours à corriger.** Réponse exacte transmise par la session principale :
**« oui go »**, à la question **« Tu valides son apparence et sa tenue, chaussures
comprises ? Le profil reste à corriger ; cette validation n’autorisera pas
automatiquement une nouvelle génération. »** Session
`ses_ef27d5cdcffefU62W3ufHMHm2L`. Cet accord ne valide pas la géométrie stricte des
quatre angles, ne clôt pas le stade canonique personnages et n'autorise aucun
nouveau job. Le « go » permet la préparation de la correction seulement.

Les observations et la décision en attente ci-dessous sont **le compte rendu
historique avant cet accord** ; notamment les chaussures/proportions visibles
étaient encore proposées lors de la première revue. Le détail actualisé et les
trois crops dérivés figurent dans `approval.md` et dans la note finale ci-dessous.

## Fichier et provenance

- Projet / entité existants : `project_la_pomme` / `char_001`, variante adulte.
- Sortie examinée réellement :
  `projects/la-pomme/references/generated/char_001/attempt-01/fbe7c67f_000.png`.
- SHA-256 calculé sur les bytes du PNG :
  `06d3c347e907508d69885257b08d222c465525bdacea7a993052077a3d6ea4dd`.
- Dimensions vérifiées dans le PNG : **1280 × 720 pixels**, **16:9** ; réglage
  de génération transmis : **1K**, sans upgrade 2K.
- Job transmis par la session principale :
  `fbe7c67f-895e-4333-8181-ce1967d46d49`.
- Modèle transmis : `bytedance-seed/seedream-5-0-flash`, gamme `preparation`,
  exécuté par la session principale via le projet / `cloud_batch`.
- Source réellement relue pour comparaison :
  `projects/la-pomme/art-direction/Homme fatigué dans un appartement nocturne.png` ;
  portrait approuvé lié à `char_001`, unique référence en ordre 1.
- **Une image de référence, une tentative, quatre figures dans cette image** ;
  zéro shot render et aucun retry dans cette revue.

Les informations d'exécution et de coût ci-dessous proviennent de la transmission
de la session principale ; la lecture visuelle et le hash/dimensions sont vérifiés
directement ici. Aucun nouvel audit de graphe ou de ledger n'est revendiqué.

## Identité, tenue et rendu

| Critère | Observation sur la sortie | Réserve |
| --- | --- | --- |
| Visage / identité adulte | Visage anguleux, sourcils marqués, fatigue autour des yeux, nez et mâchoire compatibles avec le portrait ; cohérence visuelle entre les trois visages visibles. | Ressemblance convaincante à cette échelle, pas preuve d'une identité exactement reproduite. Le visage frontal paraît plus sévère et frontalement construit que l'expression baissée de la source ; détails fins limités par la taille des visages dans la feuille. |
| Cheveux | Cheveux courts foncés à mèches irrégulières, silhouette désordonnée conservée ; pas de coiffure lisse ou longue ajoutée. | Le contour des mèches varie avec les vues ; la fidélité mèche par mèche n'est pas établie. |
| Barbe / fatigue | Barbe courte et moustache visibles, cernes/ombres et traits adultes conservés ; aucun rajeunissement manifeste. | Densité et implantation exactes difficiles à certifier à cette résolution. Aucune couleur précise des yeux inférée. |
| Vêtements / palette | Veste et pantalon anthracite, chemise gris clair ouverte, sans cravate, ceinture sombre : continuité générale respectée. Ombres légèrement olive, sans transformation évidente en costume vert. | Plis et coupe complète sont des reconstructions, pas des détails approuvés par extension. Les chaussures noires restent une proposition nouvelle hors champ du portrait. |
| Graphisme | Contours sombres fins et ombres peintes en facettes ; proportions réalistes et rendu dessiné semi-anime, sans photo, chibi ou 3D plastique. | Bonne continuité de langage, sans garantir un dosage stylistique identique au portrait plus grand et plus dramatique. |
| Lumière / fond | Fond gris sobre légèrement texturé, illumination comparativement diffuse et stable ; décor nocturne et rim light ambre non recopiés. Vêtements sombres globalement lisibles. | La feuille reste assez sombre ; les détails du visage sont moins lisibles que dans le portrait source. |
| Anatomie / cadrage | Quatre corps entiers distincts, cheveux et chaussures inclus, poses debout calmes, bras relâchés, mains vides ; échelle et ligne de sol globalement cohérentes. | Aucun défaut anatomique majeur évident à cette échelle ; doigts et anatomie fine non certifiés. Proportions complètes et dos restent des complétions exploratoires non approuvées. |

Pas de scène, chats, accessoires narratifs, texte, labels ou watermark visibles.
La pose neutre diffère volontairement de la posture appuyée du portrait : elle
ne devient pas un nouvel ancrage narratif ou une attitude permanente.

## Vérification des quatre vues — de gauche à droite

1. **FRONT : présente.** Corps globalement frontal, visage de face, deux côtés
   du costume et les deux mains lisibles.
2. **LEFT 3/4 : présente visuellement.** Tête et corps tournés vers la gauche
   de l'image, poitrine encore visible ; lecture de trois-quarts cohérente.
3. **LEFT PROFILE : non conforme pour le corps.** La tête s'approche du profil,
   mais le torse conserve une large surface frontale, les deux revers/parties
   avant de la veste et les deux jambes restent largement exposés. La figure
   est encore un trois-quarts, très proche de la deuxième ; ce n'est **pas un
   vrai profil latéral plein corps à 90°**. Aucun angle numérique exact n'est
   mesuré à partir du dessin. Cette vue ne doit pas être présentée comme un
   profil complet fiable pour de futurs raccords.
4. **BACK : présente.** Arrière du crâne, veste, pantalon et chaussures visibles,
   sans visage frontal ; construction du dos proposée par le rendu.

**Conclusion technique :** bon aperçu exploratoire de l'adulte et de la tenue,
mais quatre figures ne signifient pas quatre angles conformes. Le principal
écart est la troisième vue, qui duplique partiellement le trois-quarts au lieu
d'apporter le profil corporel demandé. Aucun « turnaround parfait » revendiqué.

## Une seule recommandation de correction ciblée — sans exécution

Si l'utilisateur souhaite corriger plutôt qu'accepter cet aperçu avec sa
limite : **corriger uniquement la troisième figure en vrai profil gauche de
tout le corps**, tête, épaules, thorax, bassin, jambes et pieds cohérents dans
la même orientation latérale, nez vers la gauche de l'image ; ne pas conserver
un torse trois-quarts sous une tête de profil. Préserver les trois autres vues,
l'identité, les vêtements, le rendu, l'éclairage et le format.

Ceci est une recommandation QC, **pas un nouveau prompt, une promesse de retouche
locale, un nouveau job ou un retry autorisé**. Toute nouvelle génération/correction
payante nécessiterait un nouvel accord explicite sur sa préparation et son coût.
La tentative 01 doit rester conservée, sans écrasement.

## Coût et limites de consentement

Selon la session principale : consentement utilisateur **« go »** à la demande
annonçant **0,018 USD**, plafond de job **0,020 USD**, **une tentative**, sans
retry. Le helper de record a retrouvé un **coût réel de 0,018 USD** pour cette
génération. Plafond projet transmis : **30 USD** ; disponible annoncé :
**29,982 USD**, dans le périmètre suivi ComfyUI/OpenRouter.

Le coût de l'essai GPT externe ayant fourni le portrait reste **inconnu et
séparé** : il n'est ni inclus arbitrairement ni supposé nul. Cette revue ne
modifie aucune estimation, décision, autorisation ou ligne de ledger.

## Décision artistique en attente

La session principale présentera la sortie via l'image inline du chat ; aucun
retry d'outil navigateur ici. Faire distinguer à l'utilisateur :

- reconnaît-il l'adulte du portrait dans le **visage, les cheveux et la barbe** ?
- accepte-t-il le **rendu et les tons** du costume/chemise, ainsi que les
  **chaussures et complétions hors champ**, encore proposés ?
- souhaite-t-il **conserver cet aperçu avec le défaut de profil signalé**, ou
  envisager la seule correction ciblée décrite ci-dessus, sans dépense automatique ?

Aucune réponse ni approbation inventée. **Aucun crop, inscription dans
`references/approved-references.yaml`, modification canonique ou autre fichier**
dans cette tâche. Documents de garde relus : `docs/cloud-policy.md`,
`config/cloud-tiers.yaml`, skills `model-sheets` et `cloud-production`.

## Mise à jour après l'accord d'apparence — 2026-10-05

L'apparence adulte visible, la silhouette et la tenue complète, **chaussures
comprises**, de cette sortie sont désormais approuvées dans le périmètre de la
question citée en tête. Cela ne démontre toujours pas une fidélité biométrique
exacte ni des mesures/couleurs cachées. Le défaut du troisième panneau décrit
plus haut reste intact : ne pas le labelliser profil conforme.

Le registre conserve les trois premières sources dans leur ordre et ajoute cette
sortie complète à l'ordre 4, avec approbation d'apparence limitée. Trois crops
Pillow locaux ont été créés et réellement examinés : face, trois-quarts gauche,
dos ; chacun garde le corps entier, cheveux/chaussures et marge, sans autre figure.
Ils sont dérivés du parent approuvé, pas trois accords artistiques nouveaux.
Aucun crop du troisième panneau, aucun resize/retouche, parent inchangé.

La correction préparée séparément est **un profil isolé plein corps en 9:16**,
pas une régénération des quatre vues ; les trois vues originales restent intactes.
Le draft n'est pas encore un cloud-job validé et requiert une nouvelle demande
de consentement chiffrée par la session principale avant tout appel. Aucun job,
ledger, budget, storyboard ou fiche canonique modifié par cette mise à jour.

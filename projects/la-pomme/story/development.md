# La Pomme — brief conservé et développement proposé

## Statut et périmètre

- « La Pomme » est un **titre de travail proposé**, pas un choix explicite de l'utilisateur. Le nom du dossier est une clé technique ; changer le titre n'oblige pas à renommer les IDs.
- Gamme de préparation, **planning seulement**. Une revue budgétaire de planning existe (`preparation`, plafond 30 USD), mais ne donne aucun consentement payant. Cette mise à jour ne crée aucun consentement, média, screenplay, scène ni shot et ne modifie pas l'estimation ou la décision existante.
- La recommandation texte du fichier `config/cloud-tiers.yaml` est `openai/gpt-6-luna` ; elle **ne change pas le LLM runtime hérité**. Aucun override de modèle ni modification de configuration runtime.
- Politiques relues : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`, `docs/film-method.md`. Skills chargés : `story-development`, `cloud-production`. Base approuvée lue : `art-direction/style-brief.md`.
- Ce document distingue le brief initial, les choix explicitement acquis depuis et les propositions encore révisables. Le « ok » à la suite annoncée autorise cette synchronisation narrative, pas l'approbation du souvenir, de tous les détails ou d'une dépense.

## Brief utilisateur initial — historique conservé

Les paragraphes suivants conservent le brief initial pour provenance. Pour l'état courant, les choix acquis ci-dessous **remplacent** l'enfance chaude/délavée par une enfance froide/banale et l'ancienne possibilité de phrases par l'absence de paroles intelligibles. Ils ajoutent le retour du travail et précisent le refuge, le décor et les apparences ; aucune demande ancienne n'est effacée de cet historique.

**Cadre et présence.** En 2026, un homme d'environ 40 ans, seul dans un salon contemporain de nuit avec deux chats, regarde un vieux film des années 1990. Un principal adulte, un salon et une télévision ; quelques flashbacks limités. L'enfant est la version passée du même homme. Les autres adultes restent hors champ ; pas de foules. La fiction diffusée à la télévision doit être originale, évocatrice des années 1990, et non la reproduction d'un film protégé. Durée souhaitée : 6 à 9 minutes.

**Intention.** Introspection, solitude, validation, honte, critique, vide, amour et enfance ; léger surréalisme. Palette vert sombre, olive, jade noirci, fumée douce. Réalité vert froid ; enfance chaude et délavée ; surfaces mentales contrastées, agressives. Ces contraintes sont conservées, sans développer maintenant une direction artistique exhaustive.

**Transformation de la télévision.** D'abord le film, puis un son lointain/distordu et des fragments de son esprit : travail humiliant, chefs, regards, solitude, besoin d'amour et de reconnaissance, rejet, soi déformé. Ses problèmes le regardent.

**Trois taffes.** Première taffe : fragmentation en six surfaces mentales distinctes — travail, regards, amour, rejet, approbation des chefs, soi. Deuxième : le bruit baisse ; extinction des écrans sauf un, l'enfance — parents distants/durs, enfant attendant l'amour, sentiment de ne pas suffire. Révélation : les quêtes de succès et de validation cachent un manque d'amour ancien. Les phrases de compréhension restent possibles, pas nécessaires ; aucun dialogue n'est imposé. Dernière taffe : le dernier écran devient une pomme réelle, silencieuse, presque sacrée ; il mange ; cut noir.

**Pomme et garde-fous.** Désir, manque, origine, tentation, connaissance, blessure ; intégrer la vérité sans culpabiliser l'enfant. Fin impérativement conservée : pomme mangée, noir ; pas d'épilogue, pas de moralisation. Ne pas présenter le cannabis comme un remède ni la compréhension comme une guérison instantanée. Les trois taffes ponctuent la forme sans causalité médicale imposée. Vraie progression émotionnelle ; événement d'enfance concret, sobre, non sensationnaliste ; amour conditionnel. Chats comme ancrage réel, pas actifs simultanément.

## Choix acquis synchronisés dans l'histoire

Source de preuve : `art-direction/style-brief.md`, réponses explicites de la session principale `ses_ef27d5cdcffefU62W3ufHMHm2L` ; aucune approbation étendue par inférence.

- **Ouverture :** l'homme revient du travail en costume. La traduction intérieure entrée gauche → même salon → assise est intégrée à `beat_001`, sans extérieur, scène au travail, nouveau lieu/ID ou ajout de durée. Entrée dans une douceur mélancolique, chats rassurants, douleur sous le calme.
- **Adulte `char_001` :** visage anguleux avec cernes, cheveux bruns foncés courts désordonnés, barbe courte, costume anthracite et chemise gris clair à col ouvert sans cravate ; apparence du portrait approuvée. Aucun métier précis, taille, ethnie, couleur numérique d'yeux ou geste de retrait de veste ajouté.
- **Chats :** `char_002` tigré gris-brun ; `char_003` Persan crème. Apparences visibles approuvées avec légère harmonisation graphique acceptée mais non réalisée ; un seul chat actif à la fois, aucun placement permanent inféré.
- **Salon :** intime sans encombrement, moderne mais vécu ; parquet, table basse en bois, canapé en L gris foncé, bibliothèque/livres, plantes et objets personnels ; TV à droite face au canapé, petite lampe ambrée derrière à gauche, fenêtre sur ville au fond. Disposition visible et lumière approuvées, dimensions/hors-champ non inventés.
- **Intrusion :** reflets subtils dans la télévision et les surfaces réfléchissantes avant les six surfaces mentales. La lampe existe dès le refuge : la télévision n'est pas son unique point lumineux. Pas d'extinction de lampe imposée.
- **Enfance :** froide et banale, lumière pâle, pièce ordinaire, sans nostalgie ; même identité `char_001`, parents hors champ. Apparence enfant non fixée, souvenir du dessin toujours proposé.
- **Son :** aucune parole intelligible, narration ou TTS. Télévision lointaine/distordue, respiration, bruits quotidiens et silences possibles ; sans paroles ne signifie pas sans son. Musique non choisie, pas de coût ou de piste audio inventés.
- **Style :** semi-anime à dominante réaliste, influence lumineuse Matrix sans reproduction ; le brief de style conserve les choix visuels détaillés. Les références adulte/salon/chats restent approuvées créativement dans le chat mais **sans fichier local disponible** : aucun asset importé, chemin/hash inventé ou fidélité de génération revendiquée.

## Choix narratifs proposés — à confirmer ou modifier

1. **Durée cible : 420 secondes / 7 minutes**, dans la plage demandée. `project.yaml` et `story.format.target_duration_seconds` reprennent la même valeur positive pour l'estimation suivante. Ce n'est pas une durée montée ni un nombre de shots déduit.
2. **16:9 et 24 fps**, paramètres provisoires ; ni format demandé explicitement ni ratio final approuvé. Genre de classement : `Drama`, avec introspection et léger surréalisme décrits en prose ; aucun sous-genre enum artificiel ajouté.
3. **Personnage sans prénom pour l'instant.** Âge approximatif, métier et identité familiale non précisés ; apparence adulte/tenue et apparences des chats désormais acquises ci-dessus. Pas de noms de chats inventés ; tigré est un motif de pelage, Persan une race choisie, non une suggestion nouvelle.
4. **Souvenir du dessin de famille.** L'enfant offre un dessin en attendant d'être accueilli ; un parent pointe l'imperfection et propose une gomme, l'autre reste occupé. L'enfant corrige, mais l'affection attendue ne vient pas. Ce détail est une proposition, **pas un fait fourni par l'utilisateur**. Il rend l'amour conditionnel visible sans abus spectaculaire, flashback extensif, parent caricatural ou dialogue obligatoire. L'âge exact de l'enfant et le sexe des parents restent ouverts.
5. **Six surfaces, pas six séquences de figurants.** Dossier corrigé, reflet exposé, place vide, porte fermée, validation retirée, visage déformé matérialisent les six thèmes. Les chefs sont une autorité hors champ, sans casting supplémentaire. Les surfaces font partie de la perception du salon, non de nouveaux lieux de production déjà définis.
6. **Progression : retour du travail → refuge doux/mélancolique → distraction → reflets → examen → efforts pour plaire → épuisement → attente enfantine → regard moins accusateur → ingestion.** La révélation ne repose pas seulement sur l'apparition d'un souvenir : l'adulte abandonne le geste de corriger et regarde enfin l'enfant lui-même. L'ouverture redistribue le temps des beats existants au sein des 420 s, sans durée ajoutée ni nouvelle subdivision canonique.
7. **Son sans paroles intelligibles acquis**, aucune narration ni TTS ; l'ancienne option de phrases est remplacée. Le travail sonore précis, sa provenance et la musique facultative restent à définir, sans génération commandée.
8. **Transition écran/pomme laissée au découpage ultérieur.** Le fait narratif et la fin sont verrouillés par le brief ; méthode visuelle, variété/couleur du fruit, emplacement précis, accessoires et plans ne le sont pas.
9. **Pas de lien thérapeutique.** Les trois taffes sont des ponctuations de la forme, non des démonstrations de causalité ou une prescription. La réduction du procès intérieur est ponctuelle ; aucune amélioration de la vie extérieure n'est montrée.

## Registre narratif d'IDs stables

Ces IDs sont déclarés dans `story.yaml` ; ils doivent être réutilisés lors des étapes suivantes, pas réattribués après un changement de titre ou de prénom.

| ID | Entité déclarée | Limite actuelle |
| --- | --- | --- |
| `project_la_pomme` | Projet | Clé technique, titre provisoire |
| `story_la_pomme` | Histoire | Proposition canonique de travail |
| `char_001` | Homme, environ 40 ans en 2026 | Enfant et adulte = même personne, deux âges ; la future fiche distinguera leurs variantes |
| `char_002` | Chat tigré gris-brun | Apparence visible approuvée, détails cachés ouverts ; pas actif avec char_003 |
| `char_003` | Chat Persan crème | Apparence visible approuvée, détails cachés ouverts ; pas actif avec char_002 |
| `char_004` | Premier parent du souvenir | Visage hors champ, main visible ; identité non précisée |
| `char_005` | Second parent du souvenir | Présence hors champ, pas de foule |
| `act_001` | Se distraire, être regardé | `beat_001` à `beat_003` |
| `act_002` | Passer encore l'examen, retrouver l'attente | `beat_004` à `beat_008` |
| `act_003` | Ne plus corriger l'enfant, prendre la pomme | `beat_009` à `beat_012` |

Les 12 beats sont déclarés sous leur acte dans `story.yaml`. Aucun ID de scène, shot, lieu, prop, asset, prompt ou génération n'est inventé. Le salon, le téléviseur, le joint, le dessin et la pomme sont des éléments narratifs concrets ; leurs fiches et IDs de production viendront après le screenplay. Les figurations mentales de `char_001` ne sont pas de nouveaux personnages. Le casting interne de la fiction télévisée n'est pas créé à cette étape.

## Continuité et décisions encore ouvertes

- Même nuit ; retour intérieur par l'entrée vers le même salon, puis assise, sans visite du travail. Tenue approuvée sans cravate conservée, aucun changement de costume décidé. Le flashback proposé est bref, froid/banal sans nostalgie, non une biographie complète ni une preuve exhaustive sur les parents.
- Deux chats toujours réels, sans pouvoir symbolique ou rôle de guérisseurs ; un seul peut bouger à la fois, l'autre restant au repos.
- Les six surfaces gardent chacune leur thème ; après la deuxième taffe, seul le support de l'enfance demeure. Après la dernière, ce support devient la pomme. Pas d'écran mental restant après cette transformation.
- Besoin d'amour et insuffisance ressentie sont distincts d'une culpabilité de l'enfant. Ni pardon ni confrontation parentale exigés.
- Encore ouverts : titre, durée précise, format technique, souvenir du dessin, apparence enfant, couleur/variété de la pomme et musique. Pas de question posée dans cette délégation ; l'approbation de ces choix ne doit jamais être inventée. Paroles intelligibles désormais exclues, non une question ouverte.

## Validation effectuée

Le 2026-10-05, les deux YAML ont passé l'API réelle du dépôt `validation.validate_file(data_file: Path, schema_file: Path)`, respectivement contre `schemas/project.schema.yaml` et `schemas/story.schema.yaml`, avec `PYTHONPATH=src /usr/local/bin/python3`. Le `python3` prioritaire du PATH appartient à ComfyUI et n'a pas `jsonschema` ; l'interpréteur déjà disponible `/usr/local/bin/python3` possède les dépendances. Aucune installation nécessaire ou effectuée.

Contrôles initiaux complémentaires réussis : IDs uniques ; références `char_*` toutes déclarées ; 3 actes et 12 beats imbriqués dans leur acte ; durée positive identique de 420 s dans projet/histoire et dans la plage 6–9 minutes ; seuls les trois fichiers du périmètre initial créés alors. Ces contrôles n'impliquent ni validation créative utilisateur ni test de génération.

Synchronisation du retour du travail et de la base visuelle : story antérieure SHA-256 `1d6f8594dd21c23955ea82cce19ca2d9b204b32f280820e2160622573c2dfe4e`, development antérieur `81cc9cac3d189b3ac05b3326f3fa4f6a1dc8f136e44d5df55c599b0c66b09c9b`. Le brief initial est conservé ci-dessus, aucun ancien canon parallèle créé. Story actualisée SHA-256 **`bfd2b51651453fa33f5aeb586398ec002a33f19d009b535b843d8fe6a8f462d2`**. Validation réussie via `validation.validate_file` contre `schemas/story.schema.yaml`, avec `PYTHONPATH=src /usr/local/bin/python3`. Contrôles réussis : mêmes IDs ordonnés, toutes les références de personnages déclarées, 3 actes / 12 beats, même durée de 420 s. Projet, estimation et décision vérifiés inchangés octet pour octet.

État réel retourné par `budget.budget_state` : avant `estimated: true, reviewed: true, reason: reviewed_planning_only` ; après `estimated: false, reviewed: false, reason: invalid_or_missing_budget: Estimate does not match story_sha256`. Les fichiers existent toujours, mais le gate détecte l'estimation stale ; aucune décision supprimée ou remplacée.

## Handoff obligatoire à l'estimation et à la revue

La prochaine étape est **budget estimation → revue explicite de l'utilisateur → screenplay**. Durée utilisable pour une estimation préliminaire : **420 s**. Le dépôt expose `film-director budget projects/la-pomme` ; l'argument facultatif `--assumptions FILE` doit respecter `schemas/budget-assumptions.schema.yaml`. Comparer bas/moyen/haut des trois gammes à hypothèses communes, en distinguant illustrations de référence et images des futurs shots. Les comptes ou longueurs de clips seront des hypothèses de planning, jamais des shots inventés.

Cette délégation se limite à la story, au développement et aux notes de synchronisation du style : aucun budget/decision, screenplay ou shot modifié. La story change de hash : l'estimation existante devient attendue **stale**, même avec une durée inchangée ; son ancien `story_sha256` ne correspond plus. La décision existante est conservée comme preuve historique, pas fabriquée ou réaffirmée pour une nouvelle estimation. La session principale réestime avec le budget-agent, contrôle les hypothèses et le gate, puis obtient la revue requise liée au nouveau hash d'estimation avant le screenplay.

Conserver **70 clips de 6 s = 420 s comme hypothèse provisoire de planning**, pas comme un nombre définitif de shots, et sans IDs ni durée ajoutée pour l'entrée. L'ancien estimateur agrège automatiquement des appels de durées maximales (53 clips en préparation dans l'estimation existante) : ne pas confondre cet indicateur avec cette hypothèse de découpage. Sans paroles intelligibles, aucun TTS ; des effets/ambiances peuvent toutefois avoir un coût distinct. `audio_seconds: 0` ne convient que si aucune nouvelle source audio n'est générée ; la décision sur le sound design reste à préciser, sans musique obligatoire. Une revue de budget n'autorise pas une génération payante.

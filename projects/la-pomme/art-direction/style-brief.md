# La Pomme — cadrage de style préalable

## Mise à jour — 2026-10-05 : quatre vues adultes disponibles

`char_001` conserve son identité adulte du portrait approuvé. L'apparence adulte,
silhouette et tenue complète, chaussures comprises, de la tentative 01 ont été
approuvées séparément sur **« oui go »** ; son troisième panneau reste historiquement
non conforme comme profil. Le profil isolé corrigé de la tentative 02 est maintenant
approuvé sur **« oui »**, à la question exacte **« Tu valides ce profil pour
compléter les références de l’homme ? Après ton accord, je pourrai réunir les
quatre vues localement, sans nouvelle génération payante. »**, session
`ses_ef27d5cdcffefU62W3ufHMHm2L`. Petites différences visuelles conservées dans
la QA, sans certification biométrique ou d'un angle exactement 90°.

Le registre garde les sources GPT et approbations historiques, ajoute les deux
sorties projet dans leurs périmètres respectifs : ordre 4 pour apparence/tenue
et trois crops front/3/4/back, ordre 5 pour le **profil natif approuvé**. Les quatre
vues isolées sont donc disponibles, sans falsifier le troisième panneau initial.
Les sorties projet sont Seedream 5 Flash `preparation` ; cela n'attribue ni modèle
ni coût connus aux sources GPT externes. Cumul transmis ComfyUI/OpenRouter :
0,036 USD pour les deux générations, coût GPT externe inconnu et séparé.

Réunion locale autorisée :
`references/assembled/char_001/adult-turnaround.png`, 1280 × 720, **front → left 3/4
→ profil gauche corrigé → back**. Trois anciens panneaux pixel-identiques ; profil
réduit proportionnellement/recadré sur le fond gris uniquement, pas étiré, recolorisé
ou rééclairé. Dérivé local de sources approuvées, **pas une nouvelle approbation
directe du composite non encore montré**, donc pas d'entrée composite au registre.
Préférer les vues isolées et le profil natif pour conditioning.

Modèle image futur toujours **`bytedance-seed/seedream-5-0-flash`**, gamme
`preparation`, sans upgrade/fallback. La recommandation texte de gamme ne change
pas le runtime OpenCode. Aucun nouveau prompt, batch, dépense/ledger, planning
des chats, story/projet/budget ou étape canonique avancés ici. Références adultes
quatre angles disponibles ne signifient pas pipeline personnages complet :
apparence enfant, expressions, autres tenues/époques et autres entités restent
non accomplis. Le brief historique ci-dessous est conservé, sans réécriture.

## Statut : base visuelle fixée, art direction détaillée à venir

### Mise à jour d'import local — 2026-10-05

**Le blocage historique « fichiers locaux absents » est levé.** La session
principale a identifié et examiné les trois PNG désormais disponibles dans
`art-direction/` : `Homme fatigué dans un appartement nocturne.png` (portrait
adulte), `Salon chaleureux, chats sous les lumières nocturnes.png` (deux chats)
et `Unknown.png` (aperçu horizontal du salon). Les mentions d'absence/import
impossible ci-dessous décrivent **l'état antérieur**, pas la disponibilité actuelle.

Les approbations créatives antérieures et leurs questions exactes restent
inchangées. `references/approved-references.yaml` enregistre maintenant les sources
complètes dans l'ordre `char_001`, `char_002`, `char_003`, avec leurs SHA-256 réels
et les « oui » de la session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Les deux chats
partagent volontairement le même PNG : trois liens d'entités, deux fichiers.
Source GPT externe, modèle exact/version/coût toujours inconnus ; aucune attribution
au modèle de production. PNG conservés en place, aucun crop ni harmonisation réalisé.

Le salon `Unknown.png` est documenté et hashé dans
`references/reference-plan.md`, **sans entrée de lieu inventée** : aucun ID
canonique de location n'existe encore. Ce plan décrit les futures multi-vues,
expressions, tenues/époques et poses assis/couché des animaux, avec approbation et
crops ultérieurs. Cet import administratif n'avance ni screenplay, fiches
canoniques, storyboard ou shots ; aucun job ni consentement payant. Le budget
reste traité séparément par la session principale et le budget-agent.

Ce brief fixe une **direction visuelle globale anticipée**, à la demande de l'utilisateur. Il ne constitue pas l'étape complète d'art direction par scènes et plans et ne contourne pas le pipeline : le screenplay, les fiches d'entités, puis l'art direction détaillée restent à réaliser dans leur ordre. Aucun screenplay, scène, shot, storyboard, prompt d'exécution ou média n'est créé ici.

**Demande utilisateur, verbatim :** « je veux un style semi anime sytme matrix grine darck smarte on dois fiexer le style en 1ER ».

- Acquis : semi-anime, influence **Matrix**, vert sombre, dark, smart, style à discuter en premier.
- Choix explicite de balance, verbatim : **« rendu plus réaliste »**, réponse utilisateur dans la session `ses_ef27d5cdcffefU62W3ufHMHm2L`. La direction retenue est donc **semi-anime à dominante réaliste** ; ce choix ne valide pas toute la charte.
- Nouveau détail utilisateur, verbatim : **« un home qui rentre de travail avec un cosutume »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Acquis : `char_001`, homme d'environ quarante ans, **rentre du travail portant un costume**. Retour désormais intégré à `beat_001` de la story, par l'entrée intérieure vers le même salon, sans extérieur ni lieu de travail. Aucune profession précise, couleur, coupe ou cravate n'est déduite de cette seule demande ; l'accord distinct du portrait fixe la tenue ci-dessous.
- **Apparence adulte de `char_001` approuvée explicitement** : réponse utilisateur **« oui »** à **« tu confirmes aussi le visage, la coiffure, la barbe et le costume de l’homme sur ta première image comme apparence définitive du personnage adulte ? »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. L'accord retient le **premier portrait vertical** pour la variante adulte : visage anguleux avec cernes, cheveux bruns foncés courts à mèches désordonnées, barbe courte, costume anthracite et chemise gris clair à col ouvert sans cravate. Aucun âge exact, taille, ethnie ou couleur précise des yeux n'est inventé ; l'apparence enfant reste à définir. Preuve consignée sans message ID inventé ; aucune génération autorisée.
- **Cinq choix acquis**, réponses au question tool de la session principale `ses_ef27d5cdcffefU62W3ufHMHm2L` :
  - Entrée : **« Douceur mélancolique »** — chats et salon rassurants, douleur sous le calme.
  - Salon : **« Moderne mais vécu »** — sobre, avec livres, objets et traces de vie.
  - Intrusion : **« Reflets puis écrans »** — départ subtil dans la télévision et les reflets, puis déploiement des six surfaces.
  - Enfance : **« Froid et banal »** — lumière pâle, pièce ordinaire, sans nostalgie.
  - Audio : **« Sans paroles intelligibles »** — respiration, télévision lointaine, bruits quotidiens et silences ; ni narration ni dialogue intelligible.
- Détails du salon acquis, verbatim : **« parquet et table basse en bois ; livres, plante et quelques objets personnels ; élévision face au canapé ; »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Retenus : parquet, table basse en bois, livres, plante, quelques objets personnels et télévision face au canapé. Cette réponse ne sélectionne ni couleur du canapé ni dimensions du salon ; l'éclairage a été choisi séparément ci-dessous.
- Éclairage acquis : réponse utilisateur **« 1 »** au choix exact **1 = « Télévision + petite lampe ambrée : refuge doux ambiance verte sombre »**, plutôt que **2 = « Télévision seule »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. **Télévision + petite lampe ambrée** retenues ; position, design de la lampe et intensités paramétriques non décidés. Ce choix créatif n'est pas un consentement de génération.
- Échelle du salon acquise : réponse utilisateur **« ok »** à la recommandation de la session principale **« intime sans être encombré : refuge progressivement oppressant »**, après le choix proposé entre petit salon intime et salon spacieux, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. **Petit salon intime, sans encombrement** retenu ; aucune dimension exacte n'est fixée. Accord limité à ce choix de cadrage du lieu, pas à tous les détails restants ni à une génération.
- **Référence salon approuvée créativement** : réponse utilisateur **« oui »** à la question exacte de la session principale **« Tu valides cette image comme référence du salon — disposition, mobilier et lumière compris ? Ce sera référence décor pas plan définitif film. »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. L'accord porte sur la deuxième image, **aperçu horizontal du salon**, et sur son décor visible, pas sur l'identité de l'homme, le contenu TV, un keyframe ou une dépense. Preuve de contexte consignée ici, sans message ID inventé ; import du fichier de production encore impossible faute de chemin local.
- Références fournies : **Matrix** comme influence cinématographique et désormais **Image 1** comme référence stylistique utilisateur. Aucun anime, réalisateur ou autre film de référence n'a été ajouté.
- Historique de l'essai externe GPT : lors du commentaire **« ca laire bon sur gpt »**, seule une satisfaction était rapportée, sans image reçue à ce moment-là. Depuis, l'utilisateur a indiqué **« j'ai ajouter l'image gpt dans [Image 1] pour les chat il dois suivre le meme style »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. **Image 1 a été reçue et examinée dans le chat par la session principale** ; les observations ci-dessous sont transmises par celle-ci, sans lecture locale de l'image par ce sous-agent.
- Provenance du premier portrait vertical : utilisateur, essai externe annoncé comme GPT ; **modèle exact, version et coût UNKNOWN**, jamais supposés nuls. Aucun chemin local ni copie de fichier disponible pour cette tâche ; aucun chemin d'asset inventé, aucune copie de bytes, aucune inscription dans `references/approved-references.yaml`. **Référence de style et d'apparence adulte approuvée créativement dans le chat**, mais pas encore asset de production importé, fiche multi-vues ou keyframe approuvé. Aucune fidélité du modèle de production n'est vérifiée par cet essai externe.
- Règle acquise : **les deux chats doivent suivre le même style qu'Image 1**. Choix utilisateur, verbatim : **« tigré et Persan »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Puis **« oui go »**, en réponse précise à la proposition **« tigré gris-brun et Persan crème »** de la session principale. Affectation aux IDs existants : **`char_002` = chat tigré gris-brun**, **`char_003` = chat Persan crème**. Cet accord confirme uniquement les couleurs proposées, pas toute la charte ni une génération, un batch ou une tentative supplémentaire. Yeux et autres détails non choisis restent ouverts ; aucun choix de chats réels ou fictifs n'est déduit de ces réponses.
- **Références d'apparence des chats approuvées créativement** : réponse utilisateur **« oui »** à la question exacte **« Tu valides ces deux chats comme références d’apparence, avec cette légère harmonisation graphique ? »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Accord sur l'apparence visible de `char_002` et `char_003` dans le troisième aperçu et sur la légère simplification future des poils/ombres pour rejoindre le style de l'homme. Harmonisation acceptée mais **pas réalisée** ; ni places permanentes, ni keyframe, ni dépense approuvés. Ce nouvel accord précise les détails d'apparence restés ouverts lors du seul choix des couleurs.
- Ressenti déjà exprimé dans le brief narratif : introspection, solitude, honte, vide, besoin d'amour ; tension nocturne puis dépouillement, sans guérison spectaculaire.
- « Smart » est interprété ici comme **cérébral, épuré, visuellement signifiant** : interprétation à confirmer, non intention acquise.
- **Les ajouts proposés restent `pending_user_approval`**, sauf les contraintes acquises et les approbations explicites ci-dessus : apparence adulte du premier portrait, référence décor du salon, apparences des deux chats avec légère harmonisation acceptée mais non réalisée. La base visuelle adulte/salon/chats est fixée ; ni tous les choix narratifs, ni l'art direction détaillée par scènes/plans, ni les fiches multi-vues ou keyframes ne sont approuvés par extension.

Sources lues : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`, `docs/film-method.md`, skills `art-direction` et `shot-design`, `story/story.yaml`, `story/development.md`, `budget/decision.yaml` du projet.

## Proposition de look — `pending_user_approval`

**Un semi-anime adulte aux proportions réalistes, mature et retenu : un salon vert-noir, des visages humains crédibles et lisibles, un dessin assumé avec contours fins et ombres peintes en facettes, une tension mentale portée par la lumière et le cadre plutôt que par les effets.** La dominante réaliste porte sur les proportions et la présence humaine, pas sur un rendu photographique. Image 1 précise concrètement la direction, avec un dessin plus marqué que la précédente proposition de lignes quasi invisibles ; aucun ratio arbitraire entre anime et réalisme n'est fixé.

**Progression globale issue des choix acquis :** douceur du refuge initial, mélancolie sous le calme → intrusions d'abord subtiles dans la télévision et les reflets, puis six surfaces → enfance froide et banale, sans chaleur nostalgique. Le salon moderne mais vécu et les chats restent rassurants sans devenir des guérisseurs. Le vert sombre n'impose donc pas une entrée immédiatement menaçante. Cette progression décrit des intentions globales, pas des scènes ou des plans déjà définis.

### 1. Semi-anime à dominante réaliste, sans changer l'âge ni la présence humaine

- Proportions crédibles pour `char_001`, homme d'environ quarante ans : **visage adulte anguleux avec cernes du premier portrait désormais retenu**, expression par les yeux, la bouche et la posture plutôt que par une déformation caricaturale. Pas d'âge précis ni de mensurations inférés.
- Style observé dans Image 1, selon l'examen de la session principale : **contours sombres fins clairement visibles**, ombres en facettes **cel painterly**, proportions naturelles et fond peint texturé. Cette observation remplace l'ancienne proposition de contours quasi invisibles et de gradients exclusivement naturels ; le dessin reste fin et adulte, sans gros contours caricaturaux. Aucun nombre obligatoire de niveaux d'ombre n'est fixé.
- Proportions, peau, tissus, pelage et anatomie des chats, environnement et lumière crédibles ; textures mesurées, volumes naturels, sans rendu 3D plastique. Apparences de référence adulte et chats approuvées ; parties non visibles et variantes supplémentaires ne sont pas inventées.
- Fonds légèrement peints et texturés, avec géométrie et perspective réelles : salon habitable, matières lisibles, profondeur compréhensible, sans effet de décor plat.
- Caractère du salon acquis : **petit et intime sans encombrement, moderne mais vécu**. La référence horizontale est désormais approuvée pour la disposition, le mobilier et la lumière : entrée ouverte à gauche, canapé **en L gris foncé** au milieu gauche, TV à droite face au canapé, table basse **rectangulaire en bois au centre**, parquet et tapis sombre à motifs, lampe ambrée derrière le canapé à gauche, plantes et livres, baie vitrée au fond sur une ville nocturne. Mug, bol, livres et télécommande visibles sur la table font partie du décor de référence approuvé ; leur utilisation narrative n'est pas décidée. Le lieu demeure un refuge doux avant de devenir progressivement oppressant, sans accumuler de nouveaux objets pour simuler cette oppression.
- Détails du salon encore ouverts : dimensions métriques, distances exactes, géométrie hors champ, essence du bois, titres des livres, espèces botaniques et détails non lisibles des objets personnels. Aucune photo de famille n'est inférée. **Canapé en L gris foncé et position visible de la lampe sont acquis par l'approbation du décor**, sans teinte numérique ni modèle commercial déduits. La forme visible et le rendu lumineux de la lampe sont retenus comme référence ; ses détails cachés et intensités paramétriques restent à définir. Fiches de lieu et de props, vues complémentaires, plan spatial et IDs correspondants viendront ultérieurement ; aucun n'est créé ici.
- Direction descriptive issue de la référence : **réalisme stylisé dessiné**, pas du photoréalisme ; influence anime lisible dans les contours et ombres, anatomie naturelle, sans chibi. Les détails d'application aux fiches et plans restent à valider, sans revenir à une interprétation de photo brute.
- Même langage graphique pour l'adulte, l'enfant et les deux chats ; le passé change de lumière, pas de technique de dessin. L'enfant reste la version passée de `char_001`, pas une nouvelle identité.

### Image 1 — premier portrait vertical : apparence adulte approuvée

Description transmise après examen visuel dans le chat par la session principale : portrait vertical d'un homme adulte d'environ quarante ans, cheveux bruns foncés courts avec mèches désordonnées, barbe courte, yeux fatigués et regard abaissé hors champ ; costume anthracite, chemise gris clair ouverte, sans cravate visible. Contours sombres fins, ombres peintes en facettes cel, proportions naturelles ; fond intérieur peint et texturé vert olive/noir, avec touches de lumière jaune ambre. **L'image est dessinée, non photoréaliste.**

Historique : ces traits étaient initialement des observations, sans approbation d'identité. **Ils sont désormais retenus comme apparence définitive de la variante adulte de `char_001`**, après le « oui » à la question exacte sur visage/coiffure/barbe/costume consignée plus haut. Référence visible : visage anguleux avec cernes, cheveux bruns foncés courts désordonnés à mèches, barbe courte, costume anthracite, chemise gris clair col ouvert **sans cravate**, proportions naturelles et dessin cel painterly. Ne pas substituer une chemise ivoire ou une cravate comme choix déjà validé.

Cet accord ne fixe pas la couleur exacte des yeux, la taille, l'ethnie, un âge précis ou des détails hors champ ; il n'approuve pas le cadrage vertical du film, une pose permanente de regard baissé, un turnaround ou une génération. L'enfant reste la variante passée de la même identité, **sans apparence de référence encore fournie ou approuvée**. Les touches ambre du portrait ne remplacent pas l'enfance froide et banale choisie. Aucun crop ni import local n'est réalisé ou prétendu.

### Chats — références d'apparence approuvées, détails non visibles encore ouverts

**Acquis utilisateur :** `char_002` et `char_003` suivent le même style que le portrait initial ; leurs apparences dans l'aperçu des deux chats sont désormais approuvées **avec une légère harmonisation graphique** : simplifier poils et ombres tout en conservant silhouettes et pelages distinctifs, pour rejoindre le trait fin visible et les facettes painterly de l'homme. Cette direction ne signifie pas qu'une correction a été rendue. Anatomie naturelle et palette olive/noir conservées, sans insertion photographique, grands yeux chibi ou rendu 3D plastique.

**Choix utilisateur acquis : « tigré et Persan »**, puis couleurs confirmées par **« oui go »** répondant à **« tigré gris-brun et Persan crème »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Accord créatif limité à ces couleurs, consigné avec les IDs déjà déclarés, sans en créer de nouveaux :

- **`char_002` — chat tigré gris-brun** : motif et couleur acquis ; apparence visible du troisième aperçu désormais retenue, silhouette adulte naturelle, rayures et yeux paraissant jaune-vert sous cet éclairage. « Tigré » désigne un **motif de pelage, pas une race** ; aucune race, mesure de poil ou teinte numérique des yeux n'est inférée.
- **`char_003` — chat Persan crème** : **race et couleur crème choisies**, apparence visible du troisième aperçu retenue, fourrure longue et épaisse, volume distinct et yeux paraissant ambre sous cet éclairage. Aucun détail caché du nez ou hypertype supplémentaire n'est imposé.

Les couleurs gris-brun et crème ne sont plus de simples suggestions : elles sont explicitement confirmées. Aucune autre couleur, nuance exacte ou marque de pelage supplémentaire n'est imposée. Les deux chats restent distincts ; ressemblance réelle et personnalité ne sont pas inventées comme décisions approuvées. Même style Image 1 : anatomie naturelle, contours fins visibles, ombres painterly et palette du salon olive/noir ; pas d'inserts photo, de 3D plastique ou de chibi. Repos et présences ordinaires maintenus ; **un seul chat actif à la fois**, l'autre immobile. Aucun pouvoir symbolique, aucune fiche canonique ou illustration de référence des chats n'est créé ici. Le « oui go » n'est ni un consentement payant, ni une approbation de batch ou de retry.

### 1 bis. Retour du travail en costume : acquis et traduction proposée

**Acquis utilisateur :** l'homme rentre du travail en costume ; visage, coiffure, barbe et tenue du premier portrait sont désormais approuvés pour sa variante adulte. Distinguer la tenue retenue des gestes et détails encore proposés :

- **Costume anthracite et chemise gris clair à col ouvert sans cravate acquis**, d'après le portrait approuvé. Coupe et matières visibles sont à conserver comme référence, sans marque commerciale ni textile technique inventé. Les anciennes options chemise ivoire/cravate ne sont pas retenues ; détails cachés et évolution des plis avec les gestes restent à préparer.
- Fatigue rendue par les épaules, la posture et les expressions retenues, plutôt que par un métier précis ou une biographie professionnelle inventée. Ni businessman héroïque, ni luxe publicitaire, ni silhouette de mannequin ; pas de cuir ou de trench emprunté à Matrix.
- Traduction narrative désormais intégrée à `beat_001` : retour visible par l'entrée intérieure à gauche vers le même salon, puis assise avec les deux chats et le téléviseur. Pas de rue, extérieur ou nouveau lieu ; aucun ID de lieu, scène ou shot. Le retour est acquis ; gestes précis et découpage restent à élaborer, sans approbation de plans inférée. L'ouverture redistribue les 420 s existantes, sans durée ajoutée.
- Continuité future : conserver la même apparence et suivre l'état du costume entre le retour et le salon. Une veste retirée reste une option à valider et consigner, pas un geste décidé. **Pas de cravate à desserrer dans la tenue approuvée** ; toute nouvelle variante de tenue nécessiterait une décision distincte.
- Même anatomie réaliste et dessin adulte avec contours fins visibles et ombres peintes en facettes, selon Image 1 ; vert sombre et influence lumineuse Matrix conservés. Dans le salon, **télévision et petite lampe ambrée sont les sources choisies** ; leur hiérarchie d'intensité reste proposée, et la lumière de l'entrée n'est pas fixée.

### 2. Matrix : influence de lumière, pas reproduction iconographique

Emprunter à la référence fournie une **dominante verte sombre, des contrastes directionnels et une mise en scène de la perception**. Adapter cette influence à un drame intime, non à une scène d'action ou à un récit de simulation.

Ne pas ajouter Neo, manteau de cuir, lunettes, pluie de code, bullet time ou accessoires reconnaissables. La fiction sur le téléviseur reste originale et évocatrice des années 1990 : elle n'est pas une diffusion ou une copie de Matrix.

### 3. Palette et sources lumineuses

- Présent : vert-noir, olive et jade éteint ; saturation contenue, noirs détaillés plutôt que zones bouchées.
- Éclairage du salon acquis : **télévision + petite lampe ambrée**, pour le refuge doux dans l'ambiance verte sombre ; harmonie olive-ambre et disposition lumineuse visible de l'aperçu horizontal approuvées, lampe derrière le canapé à gauche et TV à droite. L'option télévision seule n'est pas retenue. Intensités paramétriques et éclairage hors champ restent à définir ; éclairage spécifique des futurs visages et gestes encore à décliner, sans déduire de valeurs physiques de l'image.
- Continuité proposée (`pending_user_approval`) : garder la source de la lampe stable pendant les intrusions, afin que le refuge réel demeure perceptible face aux reflets et surfaces mentales. Aucun allumage, extinction automatique, clignotement ou changement d'intensité de la lampe n'est acquis.
- Peaux légèrement chaudes mais atténuées, sans teindre uniformément tous les visages en vert. « Dark » ne signifie pas illisible.
- Fumée douce et discrète, visible là où la lumière la traverse ; pas de brouillard permanent ni de halo spectaculaire. Les trois taffes restent des ponctuations poétiques, non une explication médicale.
- Enfance, choix acquis : **froid et banal**, lumière pâle dans une pièce ordinaire, sans nostalgie ; même langage graphique réaliste discrètement illustré que le présent. Ce choix **remplace** l'ancienne proposition d'ocres doux et de chaleur délavée, ainsi que l'orientation initiale d'enfance chaude du brief narratif. Évolution désormais synchronisée dans la story et le développement ; teintes exactes et source de lumière non encore approuvées.
- Surfaces mentales : contraste plus incisif et lumière plus dure, sans changer le graphisme ni multiplier de nouveaux lieux.
- Pomme : **rouge profond mat proposé** comme accent final dans le vert ; ce n'est pas une couleur demandée ou obligatoire. Variété, couleur définitive et traitement du fruit restent ouverts. Pas de halo miraculeux.

### 4. « Smart » : le cadre raconte

- Intrusion acquise : **reflets puis écrans**. Faire d'abord apparaître le trouble subtilement dans la télévision et les reflets, avant les six surfaces ; technique de transition et découpage restent à proposer. Ne pas démarrer par six écrans spectaculaires déjà omniprésents.
- Donner une fonction émotionnelle à la composition : espaces vides, place inoccupée, porte, reflet, geste répété puis interrompu. Ces motifs prolongent les propositions de la story ; ils ne sont pas approuvés par leur reprise ici.
- Faire sentir le procès intérieur par les répétitions et les variations de contraste, pas par une avalanche de glitches ou une surcharge de symboles.
- Garder le salon comme ancrage réel ; les six surfaces ne deviennent ni six foules, ni six lieux de production déjà définis.
- Laisser une respiration et une place au manque lorsque le bruit baisse. L'immobilité finale ne signifie ni victoire, ni vie réparée.

### 5. Caméra et rythme : principes futurs, pas découpage

- Plans courts de **4 à 8 secondes**, dans les limites du modèle sélectionné : une action, caméra statique ou un seul mouvement simple et lent ; coupes franches.
- Plans serrés pour rendre lisibles le regard et les microgestes ; cadres plus larges pour la solitude et le vide. Chaque choix devra être justifié dans l'art direction détaillée, et non appliqué mécaniquement.
- Pas d'orbite, de longue traversée continue, de bullet time ni de raccord dernier/premier photogramme pour simuler une caméra continue. Pour huit secondes, privilégier une caméra statique ou quasi statique.
- Peu de sujets actifs ; **un seul chat actif à la fois**, l'autre immobile. Les chats restent ordinaires, sans rôle de guérisseur.
- Aucun nombre de plans, durée de scène, focale ou ID de production n'est créé à ce stade.

### 6. Son pensé avec l'image

**Acquis : sans paroles intelligibles**, ni narration ni dialogue compréhensible. Respiration, télévision lointaine, bruits quotidiens et silences portent la présence sonore. Une ambiance télévisée étouffée, éventuellement vocale mais sans mots compréhensibles, reste compatible avec ce choix ; aucune réplique intelligible n'est autorisée par cette ambiance.

Traduction proposée (`pending_user_approval`) : silence habité, présence électrique discrète du téléviseur, son de fiction qui s'éloigne, frolements et petits bruits corporels ; morsure finale précise, sans emphase triomphale. Le retrait sonore peut accompagner le dépouillement visuel.

Ce sont des intentions, pas des pistes produites. Aucun TTS commandé ou planifié, aucune commande audio, aucune musique choisie ou promise, aucune copie de la bande-son de Matrix. Les éventuels raccords sonores seront définis avec les scènes et plans. Sans paroles intelligibles ne signifie pas absence de son ; ce choix ne fixe aucune nouvelle quantité d'audio, provenance ou coût de génération.

## Continuité et périmètre conservés

Les IDs existants `story_la_pomme`, `char_001` à `char_005`, `act_001` à `act_003` et `beat_001` à `beat_012` restent inchangés. Aucun ID de scène, shot, panel, lieu, prop, référence ou asset n'est inventé. Parents hors champ ; adulte et enfant de même identité ; deux chats distincts ; écran final devenu pomme, ingestion puis noir, sans épilogue.

Le souvenir du dessin, la durée cible de sept minutes et les autres choix proposés dans `story/development.md` restent des propositions : ce brief ne les approuve pas indirectement. Il ne transforme pas non plus l'influence Matrix en nouvelle intrigue.

**Synchronisation narrative effectuée avant le screenplay :** retour intérieur du travail en tenue approuvée, douceur mélancolique, salon moderne vécu et disposition retenue, deux chats aux apparences acquises, reflets puis six surfaces, enfance froide et banale et absence de paroles intelligibles désormais repris dans `story/story.yaml` et `story/development.md`. La lampe ambrée est présente dès l'ouverture ; la phrase faisant de la TV le seul point lumineux est corrigée, sans extinction prescrite. IDs et durée de 420 s conservés ; aucun nouveau lieu, scène ou shot. Le souvenir du dessin reste proposé et la couleur de la pomme ouverte. Le changement de hash de story rend l'estimation existante stale : contrôle/réestimation par la session principale et le budget-agent, puis revue liée au nouveau hash d'estimation avant d'avancer. Aucun hash de story ne remplace `estimate_sha256` ; aucune estimation/décision n'est modifiée par cette synchronisation.

Ce livrable est du Markdown préparatoire. Aucun schéma d'art direction dédié n'est présent dans `schemas/` ; aucune validation de schéma n'est revendiquée pour ce document, et aucun YAML ou schéma fictif n'est créé. L'art direction formelle sera portée ultérieurement dans les champs déclarés, notamment les notes des schémas storyboard/shots réels, en citant ce brief et en conservant les mappings scène → shot et les IDs stables.

## Validation et suite, sans génération maintenant

1. **Confirmer la charte globale sur texte**, en intégrant la balance réaliste déjà choisie : les modalités de stylisation, le ressenti « cérébral, épuré » et les détails proposés restent à confirmer ou corriger. Si l'utilisateur souhaite préciser ses références, demander ses propres images ou exemples ; ne jamais en inventer. Ne pas redemander la balance déjà tranchée.
2. La synchronisation du retour du travail et des choix acquis est réalisée dans la story. Prochaine étape : contrôler/réestimer le budget sur cet état narratif et renouveler la revue requise liée à l'estimation, puis seulement reprendre screenplay, entités, art direction détaillée, références modèle et storyboard/shots avant les keyframes. La validation de ce brief ne dispense d'aucune étape ; aucun screenplay n'est créé dans cette mise à jour.
3. Pour de futures illustrations en gamme actuellement sélectionnée `preparation`, le modèle image configuré est exactement **`bytedance-seed/seedream-5-0-flash`**, avec **1K par défaut**. Cette mention est une orientation de planning, pas une promesse de disponibilité ou de fidélité validée. Un seul modèle image de cette gamme ; ni benchmark des trois gammes, ni route legacy sans opt-in explicite.
4. Un éventuel **aperçu de style** serait une option future séparée, comptée distinctement des références et des images de shots. Aucun aperçu ni image supplémentaire n'est ajouté au budget approuvé sans estimation et nouvelle revue adéquates. Aucun prix de job n'est établi ici.
5. Toute future génération payante exige sa préparation effective, des artifacts prompt/média séparés et un consentement explicite couvrant modèle, paramètres, tentatives, coût estimé et plafond. L'accord actuel de `budget/decision.yaml` porte uniquement sur le planning (`preparation`, plafond de 30 USD), **pas sur les dépenses**. Aucun consentement de génération n'est enregistré ici.

Dans cette synchronisation, seuls la story, son développement et les notes de ce brief changent ; projet, estimation et décision budgétaire restent intacts. Aucun appel ComfyUI, batch, installation, téléchargement ou rendu ; aucun changement de modèle ou route. `openai/gpt-6-luna` reste une recommandation texte, pas un override du runtime hérité.

## Récapitulatif des choix acquis — cinq lignes

1. **Style :** semi-anime adulte aux proportions réalistes, contours fins visibles et ombres en facettes cel painterly selon Image 1 ; Matrix, olive/noir et accents ambrés, sans photoréalisme.
2. **Homme et entrée :** `char_001` adulte du premier portrait approuvé : visage anguleux/cernes, cheveux bruns foncés courts désordonnés, barbe courte, costume anthracite, chemise gris clair col ouvert sans cravate ; environ quarante ans, retour du travail, douceur mélancolique.
3. **Salon et lumière :** **petit, intime sans encombrement, moderne mais vécu** ; aperçu horizontal approuvé pour disposition/mobilier/lumière : entrée gauche, canapé en L gris foncé, table rectangulaire en bois au centre, parquet et tapis, plantes/livres/objets, baie vitrée sur ville nocturne, TV droite face au canapé et lampe ambrée derrière à gauche.
4. **Chats :** `char_002` tigré gris-brun et `char_003` Persan crème ; apparences visibles du troisième aperçu approuvées avec légère harmonisation graphique vers le portrait, non encore réalisée ; présences ordinaires, un seul actif à la fois.
5. **Traversée et son :** reflets puis six surfaces ; enfance froide et banale, lumière pâle sans nostalgie ; sans paroles intelligibles, respiration, TV lointaine, bruits quotidiens et silences.

### Points réellement encore ouverts

- **Apparence enfant de `char_001`**, vues adultes complémentaires, détails non visibles et gestes vestimentaires. Visage/coiffure/barbe et tenue adulte du premier portrait ne sont plus ouverts ; aucune taille, ethnie, couleur précise d'yeux ou âge exact n'est déduit.
- Détails des chats non visibles, vues complémentaires, mesures exactes et éventuelle ressemblance réelle ; apparence visible et légère harmonisation graphique désormais approuvées, sans valeur numérique de couleur ou anatomie cachée inventée. Aucune personnalité ni place permanente approuvée n'est déduite des poses.
- **Dimensions exactes** du petit salon intime, distances métriques, géométrie hors champ, essence du bois, livres précis, espèces de plantes et détails non visibles des objets personnels. Canapé en L gris foncé, table rectangulaire centrale et disposition visible ne sont plus des choix ouverts ; aucune dimension cachée n'est inventée.
- Détails cachés de la lampe, intensités paramétriques et lumière hors champ de l'entrée ; forme, position et rendu lumineux visibles sont retenus dans la référence décor. Maintien stable de la lampe pendant les intrusions seulement proposé, sans extinction automatique approuvée.
- Interprétation cérébrale de « smart », modalités détaillées d'application du style et caméra, souvenir du dessin, couleur de la pomme, durée cible et paramètres techniques proposés ; musique non choisie.

**Références approuvées créativement : adulte du premier portrait, salon de l'aperçu horizontal, apparences des deux chats avec légère harmonisation acceptée mais non réalisée.** Toutes restent des attachments visibles dans le chat, examinés par la session principale, sans fichier local disponible pour import de production. Aucun path, hash, crop, turnaround ou entrée de schéma fictive n'est créé. Ces accords, ainsi que les réponses antérieures sur couleurs, lumière et échelle du salon, ne valident ni les points encore ouverts, ni un batch, retry, média ou dépense.

Prochaine étape : base visuelle adulte/salon/chats fixée et story synchronisée, conserver les points non approuvés comme propositions ; réestimation et contrôle de la revue budgétaire avant le screenplay, puis fiches de personnages, chats et environnement **après le screenplay**, et art direction détaillée dans l'ordre du pipeline. Cette dernière n'est pas terminée. Aucune fiche canonique, aucun nouveau modèle/ID, prompt ou média créé ici. Story et développement seuls actualisés avec ce brief ; aucun coût, estimation, projet ou décision budgétaire modifié.

## Deuxième image externe — aperçu horizontal du salon approuvé comme référence décor

L'utilisateur a ajouté une deuxième image dans le chat de la session `ses_ef27d5cdcffefU62W3ufHMHm2L`, après le prompt salon de la session principale. **Cette image a été examinée dans le chat par la session principale** ; les observations suivantes sont transmises par celle-ci, sans lecture locale par ce sous-agent. Le label d'attachment **[Image 1] a été réutilisé** : distinguer descriptivement le **portrait vertical précédent** de cet **aperçu horizontal du salon**, sans créer d'ID de référence ou d'asset. Les mentions antérieures d'Image 1 et la règle de style des chats renvoient au portrait vertical précédent.

### Observations de l'aperçu et périmètre désormais approuvé

- Image paysage 16:9 ; homme en costume à gauche, dans une entrée ouverte, cheveux et barbe visuellement cohérents avec le portrait précédent.
- Canapé gris foncé en L au milieu gauche ; télévision à droite dirigée vers le canapé ; table basse rectangulaire en bois au centre, avec mug, bol, livres et télécommande.
- Parquet et tapis sombre à motifs ; lampe ambrée derrière le canapé à gauche ; plante à grandes feuilles derrière ; étagère de livres à droite avec une plante retombante.
- Grande baie vitrée au fond, vue sur une ville de nuit ; **aucune pluie visible**. Ni météo pluvieuse ni lieu urbain précis ne sont déduits de cette observation.
- Personnage aux contours anime plus marqués que le fond détaillé, painterly et quasi réaliste ; harmonie olive-ambre. Cette différence de traitement est observée, pas validée comme dosage définitif pour toutes les entités.
- Des **figures humaines sont clairement visibles à la télévision**. Aucun film n'est identifié ; provenance et droits du contenu représenté inconnus.
- Chats absents : cohérent avec un aperçu de décor, **pas un plan final**. Cette absence ne retire pas les deux chats de l'histoire ni les choix acquis tigré gris-brun/Persan crème.

Historique : lors du simple ajout, cette image n'était pas encore approuvée. **L'utilisateur a depuis répondu « oui »** à **« Tu valides cette image comme référence du salon — disposition, mobilier et lumière compris ? Ce sera référence décor pas plan définitif film. »**, dans la session `ses_ef27d5cdcffefU62W3ufHMHm2L`. Cette approbation créative réelle porte désormais sur le décor visible : géométrie et disposition représentées, canapé gris foncé en L, table rectangulaire centrale et ses objets visibles, parquet/tapis, baie vitrée/vue ville, plantes/livres et lumière olive-ambre avec lampe derrière le canapé à gauche. Les espèces botaniques, dimensions cachées et autres caractéristiques non lisibles ne sont pas déduites de cet accord.

**Exclusions de l'accord :** homme présent dans l'image et identité physique exacte, contenu affiché à la télévision, météo non visible, dosage graphique définitif de chaque personnage, cadrage définitif du film, keyframe de shot, vidéo, feuille modèle multi-angles et génération payante. Chats toujours requis dans le film malgré leur absence de l'aperçu. Le décor approuvé reste petit/intime sans encombrement et moderne mais vécu ; aucune extension de lieu n'est créée.

### Référence décor retenue et préparation ultérieure

**Layout, mobilier visible et harmonie lumineuse retenus comme référence décor**, conformément au « oui » utilisateur. Ils serviront de base aux vues complémentaires et au plan au sol, sans inventer les parties cachées. **Contenu TV exclu de l'approbation : à recréer en fiction originale** évocatrice des années 1990, sans recopier les figures affichées ni supposer leurs droits acquis. Les personnages, chats et fonds devront rester cohérents avec le style choisi, sans inserts photographiques, 3D plastique ou chibi.

Cet aperçu n'est ni une feuille de décor multi-vues, ni un plan au sol, ni un keyframe de shot final. Des feuilles de décor sous différents angles et un plan au sol seront nécessaires aux étapes ultérieures, après screenplay et définition des entités, pour fixer les ancrages spatiaux et préserver les futurs mappings scène → shot. Leur mention n'autorise aucun rendu maintenant.

### Provenance et limites inchangées

Source utilisateur : essai externe annoncé comme **GPT** ; modèle exact, version et coût **UNKNOWN**, jamais zéro par défaut. **Approbation créative de référence décor enregistrée dans ce brief avec contexte et réponse réelle**, sans message ID inventé. Aucun chemin local de cette deuxième image n'est disponible : import d'asset de production encore bloqué, aucun asset copié, chemin ou hash inventé, aucune entrée invalide dans `references/approved-references.yaml`. L'absence d'import ne nie pas l'approbation créative ; celle-ci ne rend pas le fichier disponible aux workflows. Aucun test du modèle configuré n'est revendiqué.

Historique de l'approbation décor : cette mise à jour antérieure se limitait au brief, sans modification de la story ou du budget. La synchronisation narrative ultérieure décrite plus haut actualise désormais la story, mais conserve projet, estimation et décision ; aucun prompt d'exécution, média, job ou consentement payant créé.

## Troisième image externe — aperçu des deux chats approuvé comme références d'apparence

L'utilisateur a d'abord annoncé l'ajout de cette image sans approbation, puis a explicitement validé les références d'apparence des deux chats avec légère harmonisation graphique (preuve ci-dessous). **La session principale l'a examinée dans le chat** ; les observations suivantes sont transmises par celle-ci, sans lecture locale par ce sous-agent. Le label **[Image 1]** est à nouveau réutilisé : distinguer descriptivement cet **aperçu des deux chats** du **portrait vertical précédent** et de l'**aperçu horizontal du salon approuvé comme référence décor**. Aucun nouvel ID d'asset ou de référence n'est créé.

### Observations — apparence visible retenue, poses et décor hors accord

- Image paysage dans un salon aux bois et lumière ambrée cohérents avec l'aperçu précédent : lampe derrière le canapé à gauche, fenêtre sur la ville au fond, TV à droite et table en bois à l'avant droite. Ces observations n'approuvent ni un déplacement de la table ni une nouvelle géométrie du décor.
- **Exactement deux chats visibles** : un tigré gris-brun assis au premier plan sur le tapis, queue courbée vers la gauche, pattes distinctes, yeux paraissant jaune-vert ; un Persan crème couché sur le canapé à l'arrière gauche, fourrure épaisse, pattes avant au repos, yeux paraissant ambre.
- Proportions adultes naturelles, silhouettes et pelages bien différenciés ; fourrure très détaillée. Chats et décor paraissent plus réalistes que l'homme aux contours stylisés du portrait initial.
- Palette harmonieuse : chaleur ambrée, gris-brun et crème face au vert froid. **Cette harmonie colorée ne démontre pas une identité exacte de style** avec le portrait ni un test du modèle de production.

Couleurs et choix tigré/Persan déjà approuvés restent acquis. Après la revue explicite, **l'apparence visible des deux chats est retenue comme référence**, incluant silhouettes, pelages et yeux tels qu'ils apparaissent sous cet éclairage, sans surspécifier de mesures, teintes numériques ou détails cachés. **Poses et emplacements ne deviennent pas permanents** : le tigré assis sur le tapis et le Persan couché sur le canapé sont des poses de référence, pas des shots approuvés. La règle d'un seul chat actif à la fois reste applicable aux futurs plans.

### Harmonisation graphique acceptée — non réalisée

Conserver l'apparence distinctive et **simplifier légèrement les détails de fourrure et les ombres dans les futures références**, pour rapprocher les chats du trait fin visible et des facettes painterly du portrait. Cette harmonisation est approuvée créativement mais **aucune correction n'a été générée ou réalisée**. Ni correction automatique, ni nouveau rendu, ni modification de cette image ne sont autorisés par cet accord de référence. Aucun aspect de personnalité n'est déduit des poses.

**Statut : références d'apparence de `char_002` et `char_003` approuvées créativement, avec légère harmonisation graphique.** Preuve : réponse utilisateur **« oui »** à **« Tu valides ces deux chats comme références d’apparence, avec cette légère harmonisation graphique ? »**, session `ses_ef27d5cdcffefU62W3ufHMHm2L`, sans message ID inventé. Cet accord distinct de celui du salon n'approuve ni modification du décor, ni placements permanents, ni keyframe, vidéo, feuille modèle multi-vues, média final ou dépense. L'apparence adulte du premier portrait a depuis été approuvée **par son propre accord distinct**, sans extension à l'enfant, au souvenir du dessin, à la pomme ou au contenu TV.

Source utilisateur, essai externe annoncé comme GPT ; modèle exact, version et coût **UNKNOWN**, jamais zéro par défaut. Approbation créative réelle enregistrée ici, mais **aucun fichier local disponible pour l'import de production** : aucune copie ni crop réalisé ou prétendu, aucun chemin ou hash d'asset inventé, aucune entrée invalide dans `references/approved-references.yaml`. Historique : l'approbation des chats avait seulement modifié ce brief. Leurs choix sont maintenant synchronisés dans la story, sans prompt d'exécution, média/job, consentement payant ou modification de projet, estimation et décision.

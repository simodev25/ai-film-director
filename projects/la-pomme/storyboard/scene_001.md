# La Pomme — Storyboard, scène 1 : le retour (`scene_001`)

**Statut : APPROUVÉ par l'utilisateur le 2026-10-06** (« ok go »), avec les ajustements plans 08 et 10 enregistrés dans `storyboard.yaml` et le scénario.
Données : `storyboard/storyboard.yaml` (`storyboard_la_pomme`, panels `panel_001_01` → `panel_001_10`).
Art direction : `art-direction/scene_001.md`. Screenplay v2 approuvé, scène 1 seulement.
Planning uniquement : aucune image, vidéo, prompt de modèle ou dépense.

**10 plans · 48 s** (ton rythme approuvé faisait ≈ 46 s ; adapté à la grille 4/6/8 s du modèle vidéo
de préparation). Un plan = une action, caméra fixe ou un seul mouvement simple, coupes franches.

## Côté caméra (règle des 180°)

- **Axe** : la ligne **porte d'entrée (bas gauche du plan) → TV (mur droit)**.
- **La caméra reste toujours du côté de la baie vitrée.** À l'écran : **porte et Marc à droite, TV à gauche** ;
  Marc regarde vers la gauche ; les chats vont vers lui (vers la droite / vers le fond).
- Lumière qui en découle : **vert TV toujours depuis la gauche**, **ambre de la lampe depuis la droite/l'arrière-droite**.
- On voit le côté gauche de Marc, comme ses vues approuvées trois-quarts et profil gauche.

## Découpage

| Shot | Durée | Cadre | Mouvement | Action | Lumière | Son |
|---|---|---|---|---|---|---|
| shot_001_01 | 6 s | Large extérieur, baie au centre | Avancée lente vers la vitre | Pluie ; la caméra s'approche | Ville froide sur le verre, ambre à droite | Pluie sur la vitre, ville lointaine |
| shot_001_02 | 6 s | Rapproché sur la vitre → salon | Avancée qui traverse la vitre | La porte s'ouvre au fond à droite | Gouttes froides → ambre ; rai du couloir | Pluie étouffée ; porte au loin |
| shot_001_03 | 4 s | Moyen large vers l'entrée | Fixe | Marc entre et referme la porte | Le rai du couloir s'éteint, ambre | Porte qui se ferme, pas |
| shot_001_04 | 6 s | Bas, jambes de Marc | Fixe | Le tigré se frotte contre ses jambes | Ambre au sol, reflets de pluie | Miaulement, ronronnement |
| shot_001_05 | 4 s | Bas, depuis le tapis | Fixe | Le Persan descend du canapé et s'approche | Ambre sur la fourrure crème | Pattes qui atterrissent |
| shot_001_06 | 4 s | Moyen, Marc vers la caméra | Fixe | Il passe sans regarder les chats | Ambre de côté, visage mi-ombre | Pas ; miaulement sans réponse |
| shot_001_07 | 4 s | Moyen sur le retour du canapé | Fixe | Il se laisse tomber sur le canapé | Ambre derrière lui | Chute, expiration |
| shot_001_08 | 4 s | Moyen large : Marc à droite, TV à gauche | Fixe | Il prend la télécommande, la pointe et allume la TV | Ambre → le vert de l'écran arrive sur lui | Clic, grésillement, TV |
| shot_001_09 | 4 s | Rapproché, visage 3/4 | Fixe | Il regarde l'écran, immobile | Vert à gauche, ambre derrière | TV étouffée années 90, pluie |
| shot_001_10 | 6 s | Plan de dos, derrière Marc, vers la TV | Fixe | Marc immobile face à la TV ; les chats à côté de lui | Contre-jour vert, ambre à gauche | TV étouffée, pluie, ronronnement |
| **Total** | **48 s** | | | | | |

Correspondance avec ton rythme approuvé : moment 1 → 01 · 2 → 02 · 3 → 03 · 4 → 04 · 5 → 05 + 06 ·
6 → 07 · 7 → 08 · 8 → 09 + 10.

## Chats et personnages

- Un seul chat actif à la fois : tigré (04) puis Persan (05) ; ensuite immobiles. Chats naturels.
- Départ : tigré couché sur le tapis, Persan couché sur la section longue du canapé. Fin : tigré sur le tapis,
  Persan assis au sol vers l'entrée (petite ellipse hors champ pendant 07–09).
- Marc garde sa tenue : costume anthracite, chemise gris clair col ouvert, sans cravate, chaussures noires.
- TV : fiction originale façon années 90, aucune œuvre réelle.

## Risques techniques (dits franchement)

1. **Traversée de la vitre (shot_001_02)** : risque élevé en vidéo. Le modèle peut s'arrêter devant
   la vitre, faire « fondre » le verre, déformer la pièce pendant le passage, ou ignorer la porte qui s'ouvre
   (petite au fond du cadre). Options, à choisir plus tard : (a) essai tel quel ; (b) image de début +
   image de fin du même plan (possible avec le modèle vidéo de préparation, pas avec celui de tests) ;
   (c) repli : coupe franche sur la vitre, le plan 02 commençant juste derrière les gouttes. Pas de faux plan
   continu par chaînage d'images entre 01 et 02 : 02 est un nouveau cadrage dans l'axe.
2. **Angle « depuis la baie »** : tes vues approuvées du salon sont toutes prises depuis l'entrée. Le mur de
   l'entrée (porte, porte-manteau) n'est fixé que par le plan au sol ; risque d'incohérence aux keyframes.
3. **Façade extérieure** (01, 10) : non définie par les références ; proposition minimale.
4. **Chats vers la droite** : leurs vues approuvées regardent vers la gauche ; on les utilise pour l'identité,
   sans image miroir (le pelage du tigré n'est pas symétrique).
5. Porte qui s'ouvre vers l'intérieur côté baie (selon le plan) : le battant cache un instant Marc — prévu.

## Questions pour toi

1. Plan final : **extérieur à travers la vitre** (miroir de l'ouverture, proposé) ou **intérieur** ?
2. Tu as une référence à toi pour l'ouverture sous la pluie ? Sinon on reste sans référence externe.
3. Lumière du couloir : **faible et neutre — choisie par l'utilisateur**.
4. 48 s au lieu de ≈ 46 s, ça te va ?

Après ta validation : `shots.yaml`, puis prompts d'images (étapes séparées). Rien n'est généré sans ton accord.


## Décisions utilisateur (2026-10-06)

- Plan 10 : « la caemra derire luit ver la tv » → plan de dos, derrière Marc, vers la TV.
- Couloir : « Faible et neutre (Recommandé) ».
- Storyboard : pas encore validé ; l'utilisateur a demandé à le voir.

- Visuel gratuit : `scene_001-camera-plan.png` (draw_camera_plan.py, sans IA ni coût) — placement caméra des 10 plans sur le plan approuvé.
- Plan 8 : « c'est luit qui va alumer la la TV » → plan moyen large où l'on voit Marc allumer la TV.
- Plan 10 : « les chats sont actoté » → chats à côté de lui (tigré sur le canapé contre lui, Persan à ses pieds).

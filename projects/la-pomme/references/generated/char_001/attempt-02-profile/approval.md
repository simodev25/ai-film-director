# `char_001` adulte — approbation du profil corrigé

Date : **2026-10-05**. Session source : `ses_ef27d5cdcffefU62W3ufHMHm2L`.
Preuve de réponse transmise par la session principale, sans message ID inventé.

**Question exacte :** « Tu valides ce profil pour compléter les références de
l’homme ? Après ton accord, je pourrai réunir les quatre vues localement, sans
nouvelle génération payante. »

**Réponse exacte : « oui ».**

## Asset approuvé et périmètre

Profil adulte gauche plein corps de l'identité existante **`char_001`**, projet
`project_la_pomme`. Image native :
`references/generated/char_001/attempt-02-profile/4a1494bf_000.png`,
**720 × 1280** ; SHA-256 :
`4e5ccd3a03574eeec15c93f9d4841f599a1c239b7f33d74dac1346a1252150ac`.
Chemin relatif à `projects/la-pomme`.

Cette nouvelle vue telle que présentée est acceptée pour compléter les références
adultes. La QA conserve les petites différences de mèches/modelé facial et le
léger décalage naturel des pieds ; aucune fidélité biométrique parfaite ou mesure
d'un angle exactement 90° n'est certifiée. Tenue anthracite, chemise gris clair
col ouvert sans cravate et chaussures noires, même identité adulte, sans mesures,
ethnie ou couleur exacte des yeux ajoutées.

Entrée **ordre 5** de `references/approved-references.yaml`. Son `view: profile`
pointe vers le **PNG natif lui-même** : aucun crop/resampling déclaré à tort.
Cette image n'est pas une feuille quatre vues ; `sheet_type` est donc omis.
Pour un conditioning de profil, privilégier ce fichier isolé natif plutôt que
la grille ou le panneau réduit.

## Provenance et accords distincts

Selon la session principale : `bytedance-seed/seedream-5-0-flash`, gamme
`preparation`, réglage **1K 9:16**, correction unique par son batch projet,
portrait initial approuvé comme seule image de conditioning. Le consentement
payant de lancement était **« Oui, lancer la correction »**, pas l'ancien
« oui go » d'apparence/tenue. Le présent **« oui »** approuve le résultat et
autorise la réunion locale ; **aucun de ces accords ne couvre un autre job**.

Coût réel transmis du helper : **0,018 USD** pour cette correction ; cumul
ComfyUI/OpenRouter **0,036 USD**, disponible transmis **29,964 USD / 30 USD**.
Source GPT externe initiale : modèle/version/coût inconnus, périmètre séparé,
pas coût nul ni provenance Seedream. Aucun coût ou ledger modifié ici.

## Assemblage local autorisé, pas nouveau rendu

- Fichier dérivé : `references/assembled/char_001/adult-turnaround.png`,
  **1280 × 720**, une rangée **front → left 3/4 → profil gauche → back**.
- Front/3/4/back : anciens crops 320 × 720 collés **pixel pour pixel** ;
  aucune retouche ou nouvelle génération, sources conservées.
- Profil : réduction proportionnelle **720 × 1280 → 405 × 720**, facteur
  **0,5625**, filtre **LANCZOS**, puis box centre `[42, 0, 362, 720]` dans
  l'image réduite. Seules des marges de fond gris sont retirées ; cheveux,
  corps et chaussures restent entiers, constaté par lecture visuelle.
- Panneau conservé séparément :
  `references/assembled/char_001/profile-panel.png`, 320 × 720.
- Aucun étirement, relight, recolorisation ou harmonisation. Les variations
  de fond/lumière entre les deux rendus peuvent donc rester perceptibles.
- Métadonnées de sources/hashes/transforms :
  `references/assembled/char_001/metadata/assembly.json`.

Le composite n'a pas encore été montré dans le périmètre de cet accord : **pas
de nouvelle approbation artistique directe prétendue ni d'entrée composite dans
le registre**. Les quatre vues sources sont approuvées séparément via les
entrées 4 et 5 ; la session principale peut présenter cette réunion technique.

Assemblée avec Pillow déjà disponible : aucun nouvel appel payant, installation,
prompt, batch, réservation ou ledger. Originals et trois anciens crops gardés
intacts. Étape canonique personnages non déclarée complète : enfant, expressions,
autres tenues/époques et autres entités restent hors de cette tâche.

## Contrôles effectués

Registre validé contre `schemas/approved-references.schema.yaml` avec le module
réel `src.validation`, `jsonschema` et contrôle des dates, sous
`PYTHONPATH=src /usr/local/bin/python3`, sans installation. Les quatre premières
entrées sont identiques à leur état préalable ; tous les hashes des sources,
crops, profil, panneau et composite correspondent aux fichiers. Les trois
panneaux anciens correspondent pixel pour pixel aux crops et à leurs boxes
parent ; le panneau profil correspond exactement au transform documenté.
Profil réduit et composite réellement examinés : aucun corps/cheveu/pied coupé.
Métadonnées JSON parsées et vérifiées, sans revendication de schéma composite.

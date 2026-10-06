# `char_001` adulte — préparation d'une correction unique du profil

## Décision réelle et périmètre

Au **2026-10-05**, session source `ses_ef27d5cdcffefU62W3ufHMHm2L`, l'utilisateur
a répondu exactement **« oui go »** à :

> Tu valides son apparence et sa tenue, chaussures comprises ? Le profil reste
> à corriger ; cette validation n’autorisera pas automatiquement une nouvelle
> génération.

L'apparence adulte visible, le corps/silhouette et la tenue, chaussures comprises,
de la tentative 01 sont approuvés ; **pas sa géométrie stricte de quatre angles**.
Le « go » permet de préparer cette correction seulement. Aucun nouveau coût
n'était cité : ce n'est **pas un consentement payant**, ni une reprise du précédent
accord à une tentative. Preuve complète :
`references/generated/char_001/attempt-01/approval.md`.

## Correction ciblée et conservation

La troisième figure actuelle a la tête proche du profil mais le torse reste en
trois-quarts. Préparer **une seule image isolée plein corps en vrai profil gauche**,
nez vers la gauche de l'image, tête/épaules/thorax/bassin/jambes/pieds orientés
latéralement ensemble, pas seulement une rotation de tête. Caméra side-on,
présentation de comparaison neutre sans scène, props, chats ou labels.

**Ne pas régénérer le turnaround complet.** Garder la source entière et les trois
vues originales front / left 3/4 / back inchangées. Elles ont été cropées localement
sans appel modèle ; leurs hashes, boxes et lien parent sont enregistrés dans
`references/approved-references.yaml`, entrée ordre 4. Aucun crop profil n'est
issu du troisième panneau non conforme. Le nouveau profil éventuel sera revu
par l'utilisateur avant toute composition locale future dans un nouveau fichier,
sans écraser la tentative 01. Aucune composition réalisée maintenant.

## Prompt et référence effectivement prévue pour le modèle

- Draft : `references/drafts/char_001-profile-correction.prompt.yaml`.
- **`prompt_id: ref_char_001_profile_correction_01`**, stable pour cette correction.
  C'est un identifiant de prompt, pas une nouvelle entité canonique ;
  `entity_id: char_001`, `project_id: project_la_pomme` conservés.
- **Clé de chaîne top-level / dotted key : `prompt`.**
- **Unique asset de conditioning, ordre 1 :**
  `art-direction/Homme fatigué dans un appartement nocturne.png`, chemin relatif
  au projet ; SHA-256
  `7e85faaddab814f55012065755fc28d2651891567b642ad11053551d9aee1314`.
  Selon la session principale, ce portrait est déjà uploadé et présent dans le
  slot chargé du scaffold : aucun nouvel upload n'est prévu. L'adaptation vérifiera
  la correspondance du slot, sans prétendre l'avoir revalidée ici.
- Le look plein corps approuvé de
  `references/generated/char_001/attempt-01/fbe7c67f_000.png` est traduit **en texte** :
  costume anthracite/pantalon assorti, chemise gris clair ouverte sans cravate,
  chaussures noires mates, silhouette naturelle et graphisme retenu. **Ni la
  feuille entière ni ses crops ne sont fournis au modèle** dans ce plan. Ne pas
  prétendre à un conditioning multi-références qui n'a pas lieu.

Garder visage adulte anguleux et fatigué, cernes, cheveux courts désordonnés bruns
foncés, barbe courte ; aucun âge exact, taille métrique, ethnie ou couleur précise
des yeux inventés, pas d'embellissement. Le rendu reste dessiné semi-anime réaliste,
contours fins, ombres cel painterly à nuance olive/charbon discrète. Fond gris neutre
légèrement texturé et lumière diffuse lisible, sans recopie de la scène nocturne.

## Paramètres futurs et coût à faire accepter séparément

| Paramètre | Valeur préparatoire |
| --- | --- |
| Gamme / modèle | `preparation` / `bytedance-seed/seedream-5-0-flash` uniquement |
| Route | `comfyui_project_adapter_via_comfy_mcp` |
| Résolution / format | **1K / 9:16** : changement de format explicite pour un seul corps, pas upgrade 2K |
| Sorties / tentatives | **1 image / 1 tentative**, sans retry |
| Seed | Pas d'override explicite ; défaut existant de la route |
| Coût configuré estimé | **0,018 USD** pour la sortie ; référence 0,000 USD selon le profil |
| Plafond de job proposé | **0,020 USD, non approuvé** pour cette correction |
| Coût réel de cette correction | **Inconnu / null**, car non exécutée |

Tarif issu de `config/cloud-tiers.yaml`, `pricing_checked_at: 2026-10-05` ;
aucune génération n'est utilisée comme contrôle de prix. Compte futur distinct :
**1 illustration de référence corrective, 0 shot render**, pas quatre images.
La tentative 01 a coûté 0,018 USD selon le record transmis ; disponible annoncé
après elle : 29,982 USD sur 30 USD, périmètre ComfyUI/OpenRouter. Ces nombres
ne réservent rien pour la correction et devront être recontrôlés par la session
principale ; le coût GPT externe de la source reste séparé et inconnu.

## Gardes restant à la session principale

Le draft n'est **pas** un cloud-job préparé/validé et ne prétend pas satisfaire un
schéma shot. L'autorité après adaptation sera `schemas/cloud-job.schema.yaml`.
La session principale prépare son batch et vérifie les bindings/descripteurs live,
format 9:16, unique slot portrait, qualité/par défaut du seed, paramètres et graphe
exact sur la cible. Pas de fallback, nouvelle installation ou changement de modèle
silencieux ; incompatibilité = blocage signalé.

Avant tout appel payant : revue budgétaire valide, tarification route actuelle,
nouvelle demande chiffrée explicite portant sur **cette image, ces paramètres,
une tentative, l'estimation et le plafond**, puis autorisation/hash/ledger du job
par la session principale. L'accord d'apparence et ce draft ne les remplacent pas.
Une seule correction ciblée puis re-review, pas de retry automatique.

Aucun job, nouveau consentement payant, budget, story, projet ou stade canonique
modifié ici. Documents relus : `docs/cloud-policy.md`, `config/cloud-tiers.yaml`,
`docs/film-method.md`, skills `model-sheets` / `cloud-production` et schéma réel du
registre. Les trois sources historiques restent intactes et d'origine GPT externe ;
seule la quatrième entrée a la provenance Seedream documentée dans ses notes.

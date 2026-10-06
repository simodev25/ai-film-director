# La Pomme — prix technique, une image exploratoire future

**Lecture tarifaire publique uniquement. Aucun consentement payant, aucune
réservation ni génération.** Le « go » transmis autorise seulement le travail
technique. Cette note n'est ni un plan de job canonique ni une décision de budget.

## Prix exact vérifié le 2026-10-05

- Modèle : `bytedance-seed/seedream-5-0-flash`, gamme **préparation** inchangée.
- Route future : `/api/v1/images`, fournisseur publié **Seed**, slug/tag `seed`.
- Une sortie **1K, 16:9, n=1**, **une tentative**, avec **un seul portrait input**.
- Illustration exploratoire standalone : **1 image générée, 0 image de shot**.
  Le portrait existant est un input, pas une deuxième illustration générée.
- **0,018 USD par image de sortie + 0 USD pour cet input = 0,018 USD estimé**
  (1,8 cent USD). La sortie n'est pas gratuite ; la ligne input gratuite est
  expressément publiée par ce fournisseur.
- `audio_seconds: 0` pour ce devis d'image ; aucun audio nouveau, TTS ou musique.
- Coût réel **inconnu/null** : aucun job effectué. Plafond par job et consentement
  payant **non définis**, pas déduits du plafond global de 30 USD.

Deux **GET publics sans clé** ont fourni la preuve conservée dans
`technical-pricing.json` :

| Source officielle | Retrait UTC | SHA-256 des octets de réponse |
|---|---|---|
| `https://openrouter.ai/api/v1/images/models` | 2026-10-05T21:01:17.784067+00:00 | `93552cff32e332709384b83f97fe2112371133df395aba983080e3c4f78ca881` |
| `https://openrouter.ai/api/v1/images/models/bytedance-seed/seedream-5-0-flash/endpoints` | 2026-10-05T21:01:17.850187+00:00 | `3f61bb59eab839f93e4f21ef47470fe2595533d60466eba3dfd50664d419e2eb` |

Le catalogue général donne les capacités et le lien d'endpoints, **pas le prix**.
Le GET d'endpoints donne `output_image / image / cost_usd: 0.018` et
`input_image / image / cost_usd: 0` pour Seed. Le JSON conserve l'entrée exacte
du modèle et la réponse fournisseur complète parsée ; les hashes couvrent les
réponses HTTP reçues, pas leur présentation reformattée. Le corps complet du
catalogue n'est pas archivé. Contrôle conforme à la source config ; âge **0 jour**
à la vérification, maximum configuré **30 jours**. Recontrôler si le job est
différé ou si la route, le fournisseur ou le tarif change.

## Capacités tarifaires, pas preuve d'exécution

Le modèle **et** l'endpoint Seed publient : résolutions `1K`, `2K` ; ratio `16:9`
supporté ; `n` **1 à 1** ; références input **0 à 14** ; seed supporté ; streaming
non supporté ; aucun passthrough autorisé. La réponse endpoint publie un seul
prix par sortie, sans discriminant tarifaire 1K/2K ; aucune taille pixel n'est
inventée depuis « 1K ». Le choix préparé reste 1K, sans upgrade implicite.

Il n'y a pas de SKU séparé texte/raisonnement dans cette réponse d'image. Le
devis utilise uniquement les deux billables publiés ; cela ne rend pas gratuits
le runtime OpenCode, la planification ou les dépenses antérieures. Catalogue et
prix ne prouvent ni binding live, ni validation du graph, ni qualité/identité
Seedream, ni authenticité d'un futur reçu.

Input prévu : portrait complet approuvé de `char_001`, ordre **1**,
`art-direction/Homme fatigué dans un appartement nocturne.png`, SHA-256
`7e85faaddab814f55012065755fc28d2651891567b642ad11053551d9aee1314` selon
`approved-references.yaml`. Pas de référence chats ajoutée. L'approbation
d'apparence n'est pas un consentement de génération. Ces sources restent des
essais **GPT externes** : modèle/version exacts et coût historique **inconnus**,
jamais attribués à Seedream ou comptés à zéro.

## Budget de film conservé, pas un nouveau budget d'image

Les trois schémas `budget-assumptions`, `budget-estimate`, `budget-decision` ont
été validés. `require_budget_review(..., selected_tier='preparation',
as_of=2026-10-05)` recalcule l'estimation **en mémoire, sans écriture** et confirme
`reviewed_planning_only`. Aucun nouveau choix de gamme ou plafond n'est requis
pour ce relevé technique ; toute modification future exige une revue affirmative
correspondante.

| Gamme — estimation de film déjà revue, USD | Bas | Moyen | Haut |
|---|---:|---:|---:|
| préparation — retenue | 15,670600 | 19,588250 | 27,423550 |
| tests — comparaison seule | 52,742976 | 65,928720 | 92,300208 |
| production — comparaison seule | 105,430952 | 131,788690 | 184,504166 |

Hypothèses communes **inchangées** : 420 s, proposition 70 plans/clips de 6 s,
**82 images = 70 keyframes + provision de 12 illustrations de référence**,
3 inputs par image, vidéo sans audio natif, texte 100k input / 20k output en
contexte standard inférieur à 272k, **60 s de sons isolés non verbaux**, aucun
dialogue/TTS ; multiplicateurs bas/moyen/haut 1 / 1,25 / 1,75, réserve additionnelle
10 %. Ces 60 s appartiennent au film déjà revu, pas à ce futur job d'image ; ils
ne sont pas remplacés par 0 dans les fichiers canoniques. La provision des
12 illustrations n'est pas réduite automatiquement par les références existantes
et ce relevé ne décide pas si une future image remplacera une unité de provision.
Les agrégats CLI 53/14/53 clips sont des agrégats de calcul, pas de nouveaux IDs.

Tarifs de cette comparaison datés du 2026-10-05 (âge 0, maximum 30 jours), mêmes
sources déclarées dans `estimate.yaml`. Le présent relevé rafraîchit uniquement
la preuve **Seedream/Seed image**, pas tous les modèles du film. Coût des
références input par passe du film : préparation 0 USD ; tests 0,137760 USD ;
production 0,275520 USD. Images/références Google sont des estimations dérivées
de tokens, non des forfaits garantis. Les hypothèses de reprises ne sont pas des
probabilités empiriques ni une autorisation de retry ; le haut n'est pas une borne
de facture garantie. Un essai échoué/ambigu peut être facturable. Ici une seule
tentative est envisagée : pas de deuxième appel automatique.

Plafond de revue existant : **30 USD**, `scope: planning_only_not_spend_consent`.
Empreintes des octets YAML sauvegardés :

- estimate : `4a49770e662e28f4117c739201b67cec34d0b4a3a4873c8859699b24cedde770` ;
- decision : `85cfb88b9d12223e02d86ac53571c37144a4158087d64a06ba53b94858d62b88` ;
- assumptions : `828a14a8f02f60faa0cf05b1245d9caebe4077c4638a64b1a809fc338634bb08`.

Preuve de revue : `budget/review-consent-02.md`, session
`ses_ef27d5cdcffefU62W3ufHMHm2L`. Le préambule de `estimate.md` conserve un ancien
état de revue ; le contrôle actuel confirme la décision renouvelée. Aucun de ces
documents n'est réécrit. La commande source `film-director budget PROJECT
--assumptions FILE` existe dans `src/cli.py` ; son aide est vérifiée via
`PYTHONPATH=src python3 -B -m cli budget --help`. L'exécutable `film-director`
n'est pas présent sur le PATH de cette vérification, mais le module source est
appelable. Aucune installation ni réexécution écrivant les artefacts déjà revus
n'est effectuée.

Exclusions inchangées : taxes/frais de crédits, licences, contexte long et
raisonnement non chiffrés, coût réel du runtime LLM, essais GPT externes, calcul
local, travail humain, Foley, compositing et montage/mixage. **Musique facultative
hors devis, prix inconnu : devis séparé si demandée**, aucune génération incluse.

## Pourquoi le disponible reste inconnu

`budget/cloud-ledger.sqlite3` n'existe pas au contrôle ; aucun ledger n'est créé.
**Disponible : inconnu/null**, et non « 30 USD disponibles » ou « 29,982 USD après
l'image ». Coût historique GPT inconnu et `opening_hold_usd` / preuve d'ouverture
absents empêchent une réservation. Une facture manquante ne prouve jamais zéro.

Preuves et helpers inspectés : `docs/cloud-reference-ledger.md`,
`src/comfyui/cloud_ledger.py` (`reserve`, `claim`, `snapshot`),
`src/comfyui/cloud_adapters.py` (`authorize_cloud_job`). `snapshot()` ne crée rien
et retourne un coût inconnu si non initialisé. `reserve()` exige une valeur
monétaire d'ouverture finie non négative **explicitement rapprochée** et une
`opening_balance_reference` non vide couvrant les responsabilités externes et
historiques. Un vrai zéro n'est possible qu'avec rapprochement affirmatif et
preuve traçable ; rien n'est inventé ici. La base d'ouverture est immuable dans
cette API minimale : ne pas initialiser arbitrairement pour corriger plus tard.

## Ce qu'un futur accord payant devra réellement couvrir

1. Rapprochement des dépenses historiques/externes et preuve d'ouverture, puis
   calcul du disponible sous le plafond projet de **30 USD**. Inclure les coûts
   connus et provisions/holds non résolus ; ne pas réinitialiser l'historique.
2. Graph ComfyUI séparé préparé par l'adapter du projet, target exploratoire
   vérifiée, route/model/provider **Seed** exacts, 1K/16:9/n=1, portrait unique
   ordonné vérifié et uploadé, options live inspectées, validation du graph exact.
   Cette note ne réalise aucun de ces prérequis d'exécution à la place du main.
3. Réponse utilisateur **affirmative explicite** `scope: paid_generation_job`,
   liée à une seule tentative, coût estimé **0,018 USD** et **plafond positif par
   job** au moins égal à l'estimation. L'accord doit lier `tier`, `model`, `route`,
   `workflow_sha256`, `plan_sha256`, `estimate_sha256`, `project_id`,
   `scope_sha256`, `decision_sha256`, `target_evidence_sha256` exploratoire et
   une `consent_reference` réelle non vide. Le « go » technique et la revue de
   budget ne satisfont pas cet accord. Ni plafond par job ni texte d'accord
   approuvé ne sont fabriqués ici.
4. Réserver **tout le plafond du job**, pas seulement 0,018 USD, dans l'unique
   ledger canonique ; exposition agrégée + réserve <= 30 USD. Claim une seule
   fois avant soumission caller-owned via comfy-mcp dans la session principale.
   Aucune API de génération directe ou route de fallback.
5. Conserver le coût réel `null` et le hold si charge inconnue, échec ou ambiguïté,
   jusqu'à preuve fournisseur. Tout nouvel essai requiert une nouvelle demande
   explicite avec coûts, hash et tentative correspondants. Aucun retry automatique.

**Conclusion pour la session principale :** le prix exact de la route Seed est
**connu : 0,018 USD** pour ce seul futur rendu ; ce n'est pas un blocage « prix
manquant ». Le budget disponible et l'ouverture sont **inconnus** ; le consentement
payant et les validations d'exécution manquent. Aucune dépense n'est autorisée.

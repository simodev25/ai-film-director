# La Pomme — preuve de revue budgétaire

Date d'enregistrement : 2026-10-05.
Scope : `planning_only_not_spend_consent`.

## Source et texte utilisateur verbatim

Session source : `ses_ef27d5cdcffefU62W3ufHMHm2L`.
La session principale transmet les réponses explicites de l'utilisateur après
présentation du tableau des coûts et demande de revue. Aucun identifiant de
message non fourni n'est inventé ; la référence traçable est cette session et
ce fichier de preuve.

Première réponse, remplacée par la correction suivante :

> Préparation Haut 30 $

Correction effective, qui fait foi :

> non je veux dire Préparation Bast 30 $

## Décision et interprétation

La correction « Bast » est interprétée comme « bas », et non « haut ».
L'utilisateur retient donc la gamme **préparation** (`preparation`), avec le cas
**bas** de l'estimation existante : **15,670600 USD**, et un **plafond de 30 USD**.
Ce plafond est une limite, pas une cible de dépense, ni une demande de consommer
30 USD. Le choix précédent « Haut » est remplacé, pas conservé en parallèle.

La revue affirmative est enregistrée dans `decision.yaml`, liée aux octets
actuels de `estimate.yaml` par le SHA-256 :

```text
afb4abb27306a20b7882ef6797ab890978dae2da37ff69ee192f6ca1f5b7abf6
```

Le schéma de décision ne prévoit pas de champ `low` ou de scénario de coût :
le choix bas est documenté ici seulement. Les seuls champs de décision sont
ceux autorisés par `schemas/budget-decision.schema.yaml`.

## Estimation revue, conservée sans recalcul ni modification

| Gamme | Bas (USD) | Moyen (USD) | Haut (USD) |
|---|---:|---:|---:|
| préparation | 15,670600 | 19,588250 | 27,423550 |
| tests | 52,742976 | 65,928720 | 92,300208 |
| production | 105,430952 | 131,788690 | 184,504166 |

Hypothèses communes conservées : 420 s de film ; proposition de 70 plans de
6 s ; 82 images = 70 images de plans + provision de 12 illustrations de
référence ; 3 références en entrée par image ; vidéo sans audio natif ;
100 000 tokens input et 20 000 output ; 60 s de sons isolés non verbaux, **0 s
de dialogue/TTS**. Les 60 s représentent une provision de nouvelles sources
sonores, pas un défaut automatique lié à la durée du film. Supprimer cette
provision exigerait une nouvelle estimation avec `audio_seconds: 0` et revue.

Bas/moyen/haut appliquent les multiplicateurs 1 / 1,25 / 1,75 et une réserve
supplémentaire de 10 %. Ils représentent une incertitude comptable, pas une
permission de reprise ; les échecs peuvent être facturables et le haut n'est
pas une borne garantie. Les agrégats CLI de 53 / 14 / 53 clips ne remplacent
pas le futur découpage. Le détail préexistant reste dans `review-notes.md`.

Tarifs du snapshot config 2026-10-05, âge de 0 jour à cette revue, sources
OpenRouter déclarées dans `estimate.yaml`, limite de fraîcheur 30 jours ;
aucune actualisation réseau ni génération de vérification. Charges de
références incluses par passe : 0 / 0,137760 / 0,275520 USD ; les illustrations
de référence sont incluses dans les 82 outputs, pas gratuites. Les tarifs
Google dérivés des tokens restent estimatifs.

Musique facultative : exclue, coût inconnu, devis séparé si demandée.
Exclusions et incertitudes inchangées : raisonnement, contexte long, runtime
LLM réel, taxes/frais, licences, coûts locaux, compositing, montage/mixage,
Foley et travail humain. Aucun de ces coûts inconnus n'est déclaré nul.

## Portée et préservation

Cette décision est une **revue de planification uniquement**, jamais un
consentement à un job payant. Aucun job, génération, installation, téléchargement,
appel API de génération, retry automatique ou montée de gamme n'est autorisé
par ce fichier. Toute génération nécessitera un accord supplémentaire explicite
lié au modèle, paramètres, tentatives, coût et plafond du job ou lot concerné.

La recommandation texte de préparation `openai/gpt-6-luna` n'affecte pas le
modèle runtime OpenCode hérité. Aucun changement de runtime n'est effectué.

`project.yaml`, `story/story.yaml`, les IDs canoniques, `assumptions.yaml`,
`estimate.yaml`, `estimate.md` et `review-notes.md` restent inchangés. Les mentions
de revue manquante dans les rapports précédents décrivent leur état historique
avant cette décision ; ce fichier et `decision.yaml` consignent la revue reçue.
Aucun scénario, prompt ou média n'est créé ni avancé pendant cette étape.

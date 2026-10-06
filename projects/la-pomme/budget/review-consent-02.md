# La Pomme — preuve de revue renouvelée, 02

Date d'enregistrement : 2026-10-05.
Scope : `planning_only_not_spend_consent`.
Session source : `ses_ef27d5cdcffefU62W3ufHMHm2L`.

## Contexte transmis et réponses utilisateur verbatim

La session principale transmet les réponses réelles de l'utilisateur après
présentation de la réestimation et demande de reconfirmation. Contexte de la
question, résumé fourni par la session principale, **pas citation verbatim** :
confirmer le maintien de Préparation, estimation basse et plafond de 30 USD,
pour passer au scénario après la synchronisation de la story. La réestimation
présentée concerne le même film de 420 s ; coûts inchangés mais nouveau hash.

Réponse exacte à cette demande de maintien :

> Basse — ton choix on dois faire le Storyboard de 1 er seane

Message utilisateur suivant, exact :

> on dois fixer les personer pour le remais comme refrenece

La source traçable est la session ci-dessus, avec le contexte et les deux
réponses transmis par la session principale ; aucun message ID absent n'est
inventé. L'accord n'est pas inféré d'une permission d'outil ou d'un choix par
défaut. La réponse « Basse » confirme explicitement le scénario de coût bas
dans la demande de maintien de **préparation et plafond 30 USD** ; ces deux
valeurs viennent du contexte explicite, pas d'une sélection faite par l'agent.

La demande de storyboard et celle de fixer les personnages décrivent la suite
de planification souhaitée, sans valider des fiches, keyframes ou plans encore
inexistants, ni autoriser une génération. Cette étape n'en crée aucun et ne
dispense pas de leurs prérequis canoniques.

## Décision renouvelée et empreinte

- Gamme : **préparation**, `selected_tier: preparation`.
- Cas retenu : **bas**, estimation **15,670600 USD**.
- Plafond confirmé par maintien du contexte : **30 USD**, limite et non cible.
- Revue affirmative : `approved: true`, pour **planification uniquement**.
- SHA-256 recalculé sur les **octets sauvegardés de budget/estimate.yaml** :

```text
4a49770e662e28f4117c739201b67cec34d0b4a3a4873c8859699b24cedde770
```

`decision.yaml` est renouvelé pour cette empreinte et renvoie à ce fichier de
preuve. Le schéma ne possède pas de champ pour le cas bas : celui-ci est
documenté ici, sans clé non supportée dans la décision. Les preuves de revue 01
restent intégralement dans `history/review-01/` ; l'ancien `review-consent.md`
et les rapports antérieurs sont conservés comme historiques.

## Estimation revue, inchangée

| Gamme | Bas USD | Moyen USD | Haut USD |
|---|---:|---:|---:|
| préparation — retenue | 15,670600 | 19,588250 | 27,423550 |
| tests — comparaison uniquement | 52,742976 | 65,928720 | 92,300208 |
| production — comparaison uniquement | 105,430952 | 131,788690 | 184,504166 |

Hypothèses conservées : 420 s ; proposition de 70 clips de 6 s ; 82 images =
70 keyframes + provision de 12 illustrations modèles/références (pas de nouveaux
IDs), 3 références input/image ; vidéo sans audio natif ; tokens 100k input/20k
output, contexte standard inférieur à 272k ; 60 s de sons isolés **non verbaux**,
aucune narration ni TTS ; reprises comptables 0/25/75 %, réserve supplémentaire
10 %. Les agrégats CLI 53/14/53 clips ne sont pas le futur découpage.

Tarifs config du 2026-10-05, âge 0 jour à cette revue, sources OpenRouter
déclarées dans estimate.yaml, limite 30 jours. Références input incluses par
passe : 0 / 0,137760 / 0,275520 USD ; illustrations générées payantes. Image
Google et références : estimations token-derived, non forfaits garantis.
Texte : recommandations de la config, pas facture du runtime LLM hérité.

Musique exclue, coût inconnu, devis séparé si demandée. Inconnus/exclus inchangés :
raisonnement, tokenisation effective, contexte long, runtime/abonnement LLM,
taxes/frais, licences, essais GPT externes, coûts locaux, compositing,
Foley, montage/mixage/finishing et travail humain. Inconnu n'est pas zéro ;
les échecs peuvent être payants et le cas haut n'est pas une borne garantie.
Les approbations créatives externes ne prouvent pas la qualité Seedream ni sa
facture ; aucune réduction automatique des 12 illustrations n'est effectuée.
Le détail complet reste dans `review-update.md`.

## Portée stricte et fichiers conservés

Cette revue lève seulement le verrou **budgétaire de planification** pour la
gamme préparation sur cette estimation. Elle n'autorise aucun job ou lot payant,
retry, upgrade de gamme, installation, téléchargement ni bypass API. Une dépense
nécessitera un consentement supplémentaire explicite lié aux jobs, modèles,
paramètres, tentatives, coûts et plafonds. Aucun ledger de génération n'est créé.

Aucune réexécution de la CLI budget : estimation YAML/Markdown, hypothèses,
story et projet restent inchangés. Aucun fichier screenplay, personnage ou
référence n'est modifié par cette étape. Aucun backend ni runtime LLM changé.
Toute modification ultérieure de l'estimation, gamme ou plafond exige une
nouvelle revue correspondante ; ce consentement n'est pas une autorisation
anticipée sur une autre empreinte.

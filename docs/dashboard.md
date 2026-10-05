# Atelier — tableau de bord des films

Un petit site local en **lecture seule**, indépendant de ComfyUI, qui découvre les
projets dans un répertoire. Aucun modèle appelé, aucune génération, aucun fichier
de projet modifié, aucune approbation enregistrée depuis l'interface.

## Démarrage

Depuis la racine du dépôt, avec les dépendances Python du projet installées :

```bash
PYTHONPATH=src python3 -m dashboard.server --projects-root projects --port 8765
```

Ou avec la CLI du projet :

```bash
PYTHONPATH=src python3 -m cli dashboard --projects-root projects --port 8765
# Si le package est installé :
film-director dashboard --projects-root /chemin/vers/projects --port 8765
```

Ouvrir **http://127.0.0.1:8765**. Arrêter avec `Ctrl+C` dans le terminal.
Le serveur n'écoute que sur la machine locale ; il ne s'agit pas d'un service
authentifié à exposer sur Internet. Les fichiers des projets sont accessibles
aux autres processus/utilisateurs de la machine capables d'atteindre ce port.

## Les cinq vues

- **Vue d'ensemble** : aperçu du projet, présence des artefacts, scènes, plans,
  médias et points à vérifier.
- **Scènes & plans** : storyboard regroupé par scène, avec accès aux versions,
  prompts, personnages, lieux et accessoires d'un plan.
- **Médiathèque** : images, vidéo et audio présents sur disque ; recherche par
  chemin ou ID, filtres par type, références/rendus/non reliés ; lecteur intégré.
- **Connexions** : scène → plan, références, prompts et médias associés. Les
  rapprochements par nom de fichier sont explicitement distingués des liens
  documentés. Un trait ne prouve pas qu'une image provient d'un prompt donné.
- **Documents & suivi** : données des artefacts, résultat de validation de schéma
  quand disponible, budget et alertes. Présence ≠ validation ≠ approbation.

## Actualisation et nouveaux projets

Le navigateur relit les données toutes les **5 secondes**, lorsqu'il est visible.
Le bouton `↻` force une lecture. Ajouter un nouveau dossier dans `projects` le
fait apparaître dans le sélecteur sans modifier le code du site. Le paramètre
`?project=nom-du-dossier` conserve le projet sélectionné dans l'URL.

Les documents peuvent être incomplets : les étapes manquantes et liens inconnus
sont affichés comme tels, sans fabriquer de scène, plan ou génération.
Les références d'entités sont séparées des rendus de plans. Les versions sont
conservées ; une vignette d'aperçu n'est pas une sélection de montage ni une
validation de la version la plus récente.

Les usages comme entrée d'un autre plan sont séparés de la provenance propre
d'une image. Réutiliser un rendu comme référence ne le transforme pas en fiche
d'identité d'un personnage et ne lui transmet pas l'approbation du résultat.
L'inspecteur affiche les utilisations et l'historique des statuts lorsqu'ils
sont documentés. Les médias archivés restent dans la galerie mais ne servent
pas de vignette d'aperçu.

Le pourcentage de documentation correspond à la présence de fichiers dans les
étapes observées (documents et médias), **pas au pourcentage de film terminé**.
Les étapes distinguent prompts, fiches visuelles, images, vidéos, audio et audit
de continuité. Les schémas actuellement
disponibles peuvent ne pas couvrir tous les formats des anciens projets ; une
alerte de schéma n'entraîne aucune réécriture. Les coûts inconnus restent inconnus.

## Limites et sécurité

- Aucun accès au MCP ou à ComfyUI n'est nécessaire.
- Pas de boutons de génération, de modification ni de suppression.
- Les médias doivent rester à l'intérieur du projet : les liens symboliques
  vers des fichiers externes ne sont pas servis. Copier/relier proprement les
  assets dans les données du projet est une tâche distincte.
- Le site n'est pas un navigateur de fichiers arbitraire et ne sert pas `.env`.
- Aucun téléchargement de police ni bibliothèque front-end externe : le style
  fonctionne hors ligne avec les polices système.
- L'actualisation n'exécute ni montage, ni script, ni estimation budgétaire.

Tests spécifiques :

```bash
PYTHONPATH=src python3 -m pytest tests/test_dashboard.py
# Tests de rendu front-end sans dépendance Node supplémentaire :
node --test tests/test_dashboard_frontend.cjs
# Les tests Python peuvent aussi s'exécuter sans pytest :
PYTHONPATH=src python3 -m unittest discover -s tests -p test_dashboard.py -v
# Test facultatif en navigateur réel (Chrome déjà installé + Node avec WebSocket) :
node tests/dashboard_browser.cjs http://127.0.0.1:8765
```

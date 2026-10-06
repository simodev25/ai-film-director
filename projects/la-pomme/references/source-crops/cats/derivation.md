# Chats — dérivés locaux des apparences sources

Date : **2026-10-05**. `project_la_pomme`, IDs existants `char_002` et `char_003`.
Source unique réellement examinée :
`art-direction/Salon chaleureux, chats sous les lumières nocturnes.png`,
**1672 × 941**, SHA-256
`89015ce187d726d5560edc92d4f8f20d4f08d1406117ad2e8963a5199254b5a8`.
Chemins relatifs à `projects/la-pomme` ; le PNG parent est inchangé.

Le registre ordres 2 et 3 portait déjà l'approbation **« oui »** des apparences
visibles avec légère harmonisation graphique future. Ces dérivés n'inventent ni
accord distinct, ni approbation de futures planches, ni consentement payant.
Source externe GPT : modèle/version/coût inconnus ; aucun modèle de projet
attribué rétroactivement. Extraction via Pillow déjà installé, sans installation,
modèle, recolorisation, resampling ou stylisation des chats.

## Fichiers et rectangles

| Entité / fichier | Dimensions | Box du parent | SHA-256 |
| --- | --- | --- | --- |
| `char_002-source-raw.png` | 600 × 495 | `[470, 390, 1070, 885]` | `b60bd334c871bb383c7c183c57cf591c1be7632e4cb39ee85a24bc5dd144c67b` |
| `char_002-source-conditioning.png` | 600 × 495 | Même crop puis masque de fond décrit ci-dessous | `5245c6f54dcd1bc237c2b1dbd00ef48e1a9adf014511ac1037915ef85a05f863` |
| `char_003-source-crop.png` | 450 × 217 | `[275, 235, 725, 452]` | `9bf67e5fb35316a52929c3652f6f59c6e4abe33f02b5655425459617c79d2d54` |

Les boxes utilisent `[left, top, right, bottom]`, right/bottom exclusifs.
Tous les fichiers sont sous `references/source-crops/cats/`.

## Isolation du tigré : traitement non cible explicite

Le crop brut comprend le tigré entier visible assis, ses oreilles, moustaches,
pattes et queue annelée avec marge. Il conserve aussi une portion de fourrure et
patte du Persan en haut à gauche. Réduire le cadre pour éviter celle-ci aurait
risqué de supprimer la queue du tigré ; le crop brut est donc conservé tel quel.

Le fichier **conditioning** distinct remplace seulement le rectangle
**`[0, 0, 240, 55]` du crop**, soit **`[470, 390, 710, 445]` du parent**, par du
gris plat **RGB `[128, 128, 128]`**. Cette zone contient le fragment non cible
et du décor, **aucun pixel du tigré selon lecture visuelle du brut et du nettoyé**.
Le reste de l'image est vérifié pixel-identique au crop brut ; pas de retouche
d'apparence ou de style de `char_002`. Ce fichier n'est **pas une pure crop**,
pas un détourage complet : canapé/tapis/décor restent visibles et doivent être
ignorés par le futur modèle. Le patch gris n'est pas un choix de graphisme du chat.

## Persan : pure crop

Le crop contient le Persan crème couché visible, oreilles, pelage volumineux,
queue/fourrure latérale visible et pattes, avec marge. Aucun tigré dans ce cadre.
Pixels exactement issus de la box parent, sans masque. Les membres cachés par
la pose et le poil restent inconnus, pas reconstruits ici.

Les trois dérivés sont déclarés dans `views` des entrées originales correspondantes,
`view: other` et label de la pose **observée**, pas `front/profile` fictifs. Box
seulement pour les deux crops purs ; nettoyage du conditioning documenté dans
les notes et `derivation.json`. Les dates/verbatim/hashes parents restent ceux
de leurs approbations réelles.

## Limites

Aucune légère harmonisation du poil n'a encore été réalisée ; elle sera une
consigne des deux futurs prompts uniquement. Une image complète à six vues par
chat est planifiée, pas six appels. Nouvelle revue et consentement chiffré restent
à la session principale avant génération. Aucun upload, batch, réserve/ledger,
story, budget ou fiche canonique modifié dans cette extraction.

## Vérifications effectuées

Registre validé contre `schemas/approved-references.schema.yaml` par le module
réel `src.validation` / `jsonschema`, sous `PYTHONPATH=src /usr/local/bin/python3`.
Ordre conservé, entrées adultes 1/4/5 entièrement inchangées ; aux ordres 2/3,
anciens champs d'approbation/provenance et texte historique conservés, seulement
notes de dérivation et views ajoutés. Tous les hashes source/dérivés vérifiés.
Les deux crops purs correspondent pixel pour pixel aux boxes du parent ; le
conditioning correspond exactement au crop tigré plus le seul rectangle de masque
décrit. Trois fichiers réellement examinés : tigré intact hors masque, fragment
Persan caché, Persan entier visible sans tigré. Drafts YAML parsés et références
ordonnées/hashes/paramètres contrôlés ; aucune validation cloud-job ou live workflow.

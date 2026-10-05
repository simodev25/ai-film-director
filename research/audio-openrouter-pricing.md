# La Pomme — recherche audio OpenRouter

Date de consultation : **2026-10-04**. Recherche uniquement : GET publics et lecture du code installé, sans génération, sans appel média payant, sans accès aux clés ni modification des prompts de production.

## Conclusion importante

**Une route SFX/ambiance OpenRouter est maintenant documentée : `bytedance-seed/seed-audio-1-0`.** La documentation officielle TTS comporte une section « Non-Speech Prompts » qui autorise explicitement effets sonores, ambiances et scènes. Ne pas généraliser cette capacité aux modèles GPT Audio, Gemini TTS ou Qwen3-TTS.

La Pomme reste un film sans dialogue, narration ni chant : **aucun modèle de parole n'est nécessaire**. Le projet contient 37 YAML audio et 83 occurrences de `prompt_id`, mais ce ne sont pas 83 achats ou générations indispensables : les fonds continus peuvent réutiliser des sources, et les silences sont créés au montage. Le README audio fixe 420 secondes, dont silence intégral à 418–420 s. La pluie CPU de 50 s existe comme brouillon synthétique, pas comme Foley final.

## Modèles, prix et usage réel

Prix USD affichés, hors taxes, frais d'achat de crédits, montage et licences externes. Qualité décrite = positionnement/capacités documentés, **pas un test d'écoute de cette recherche**.

| Fonction | Modèle exact | Prix public vérifié | Exemple de coût | Route et limites | Pertinence La Pomme |
|---|---|---|---|---|---|
| SFX, ambiance, scène sonore | `bytedance-seed/seed-audio-1-0` | **0,0025 $/seconde générée = 0,15 $/minute** | 5 s : 0,0125 $ ; 30 s : 0,075 $ ; 50 s : 0,125 $ | `/api/v1/audio/speech`, entrée prompt non verbal ; omettre voix et références ; 3000 caractères max, 120 s max par requête ; MP3/PCM selon route | Candidat documenté pour pluie/room tone/Foley ; précision à l'image et qualité de chaque objet à évaluer, jamais garanties |
| Musique courte, optionnelle | `google/lyria-3-clip-preview` | **0,04 $/clip de 30 s** | 4 essais : 0,16 $ | Chat avec sortie audio ; pas le nœud AudioSpeak | Seulement si l'utilisateur ajoute une texture musicale ; pas un remplacement du Foley |
| Musique structurée, optionnelle | `google/lyria-3-pro-preview` | **0,08 $/morceau complet** | 4 essais : 0,32 $ | Chat avec sortie audio ; durée longue pilotée par prompt, ne pas assimiler à un tarif par minute | Option de composition, pas nécessaire à la partition actuelle ; aucune musique triomphale, chant ni résolution de guérison |
| Parole facultative | `google/gemini-3.1-flash-tts-preview` | Texte 1 $/M tokens ; audio 20 $/M tokens | À 25 tokens audio/s : 30 s = **0,015 $** ; 1 min = **0,030 $**, plus texte | AudioSpeak ; sortie `speech` ; modèle ancien encore catalogué | **Budget zéro car inutilisé** ; uniquement si ajout explicite d'une voix off |
| Parole facultative, économique actuelle | `google/gemini-3.8-flash-lite-tts` | Texte 0,50 $/M ; audio 6 $/M | À 25 tokens/s : 30 s = **0,0045 $** ; 1 min = **0,009 $**, plus texte | AudioSpeak ; directions via `provider.options.google-ai-studio.speech_metadata.style` | Inutile ici ; tarif promotionnel Google indiqué jusqu'au 2026-12-31 |
| Parole facultative, expressive actuelle | `google/gemini-3.8-flash-tts` | Texte 0,50 $/M ; audio 9 $/M | À 25 tokens/s : 30 s = **0,00675 $** ; 1 min = **0,0135 $**, plus texte | AudioSpeak ; style séparé du texte lu | Inutile ici ; créatif/expressif selon fiche officielle, tarif jusqu'au 2026-12-31 |
| Conversation audio | `openai/gpt-audio-mini` | Catalogue OR : texte/audio entrée 0,60 $/M, sortie 2,40 $/M | **Prix par minute non confirmé** ; ne pas reprendre le ratio de tokens Google | ChatAsk, `text` + `audio`, streaming ; pas AudioSpeak | Parole/conversation, capacité à générer tous les Foley non démontrée |
| Conversation audio | `openai/gpt-audio` | Texte 2,50 $/M entrée, 10 $/M sortie ; audio **32 $/M entrée, 64 $/M sortie** | **Prix par minute non confirmé** | ChatAsk, streaming ; pas AudioSpeak | Cohérence/naturel de voix selon description, pas un achat utile pour ce film muet |

Attention : le public catalogue OR expose bien 2,40 $/M sous `audio_output` pour GPT Audio Mini, également dans la fiche fournisseur. Cela peut être cité comme **valeur du catalogue OR**, pas extrapolé en coût minute sans ratio documenté ni vérification supplémentaire. Pour Lyria, `pricing.prompt = 0` et `pricing.completion = 0` ne signifient **pas gratuit** : les descriptions et pages tarifaires facturent par morceau.

## Trois gammes audio pertinentes

| Gamme | Choix recommandé | Budget vérifiable / exemple, pas devis film complet |
|---|---|---|
| Préparation / économique | Pluie CPU existante comme maquette ; sons enregistrés personnellement ou banque à licence contrôlée ; silence au montage ; pas TTS, pas musique requise | **0 $ d'API** pour la maquette locale, mais pas « production sonore complète gratuite » ; éventuelles licences/travail non chiffrés |
| Production équilibrée | Foley enregistré/licencié pour morsure, papier, briquet et souffle ; **Seed Audio 1.0** pour essais d'ambiances ou sources manquantes ; montage/synchronisation manuels | Exemple **10 min de sources générées = 1,50 $ par passe** ; 3 passes = 4,50 $, indépendamment de la durée finale du film ; licences séparées |
| Finition exigeante | Même route Seed si utile, sélection de prises et couches séparées ; priorité Foley spécifique, nettoyage, acoustique de pièce, calage dent/morsure et mixage ; Lyria Pro seulement si changement artistique approuvé | Même **0,15 $/min générée** pour Seed ; coût de banque/Foley/mixage **non confirmé, à devis** ; musique facultative : 0,08 $/morceau, 4 essais = 0,32 $ |

Le prix ou le nom « Pro » ne prouvent pas une meilleure qualité Foley. Les gammes se distinguent par les prises, la couverture et la finition, pas par l'achat arbitraire de trois modèles de parole. La piste finale n'a pas à employer de musique.

## Compatibilité constatée dans le code installé

Installation : `/Users/mbensass/ComfyUI-Installs/simo/ComfyUI/custom_nodes/comfyui-openrouter`.

- `src/nodes/audio/speak.py:45–50,108–116` : ID de modèle libre ; **voix vide envoyée comme absente** ; sample facultatif. Cela rend possible le prompt non vocal Seed sans forcer Kore/alloy.
- `src/openrouter/speech.py:62–80` : valide modalité `speech`, construit `input` et `response_format`, ajoute voix/référence seulement si renseignées ; endpoint `/api/v1/audio/speech` dans `src/config/openrouter.py:10`.
- `src/config/openrouter.py:25–29` : lecture publique de `/api/v1/models/{model_id}/endpoints`. **Pas de catalogue audio dédié à inventer** : découverte TTS officielle via `GET /api/v1/models?output_modalities=speech`.
- `src/openrouter/chat/audio.py:20–48` : récupère audio streaming du chat, distingue PCM vocal et fichier musical encodé. Lyria sort `text` + `audio`, pas `speech` ; choisir ChatAsk et sortie audio. Compatibilité statique seulement : aucun essai payant exécuté.
- Le GET public speech du 2026-10-04 renvoie **23 modèles**, dont Seed et Gemini 3.1/3.8 TTS. La liste chat standard contient les deux Lyria et les deux GPT Audio.
- La fiche endpoint Seed indique provider `seed`, `completion: 0.0025`, supports de références ; pour SFX les références et `voice` doivent rester absentes. Ne pas envoyer les YAML canoniques à texte vide directement : un éventuel adaptateur doit prendre l'intention sonore comme prompt et préserver leur statut non vocal.

## Sources officielles

1. https://openrouter.ai/docs/guides/overview/multimodal/tts.md — découverte speech, endpoint, **Non-Speech Prompts / Seed Audio 1.0**, unités tarifaires et limites.
2. https://openrouter.ai/api/v1/models?output_modalities=speech — GET public de 23 modèles speech et prix.
3. https://openrouter.ai/api/v1/models/bytedance-seed/seed-audio-1-0-20260630/endpoints — provider Seed, 0,0025 $/seconde.
4. https://openrouter.ai/bytedance-seed/seed-audio-1-0/pricing — meta description **0,15 $/minute**.
5. https://openrouter.ai/google/lyria-3-clip-preview/pricing — 0,04 $/clip.
6. https://openrouter.ai/google/lyria-3-pro-preview/pricing — meta description **0,08 $/morceau**.
7. https://openrouter.ai/api/v1/models — catalogue chat, architecture/prix GPT Audio et Lyria.
8. https://openrouter.ai/api/v1/models/openai/gpt-audio-mini/endpoints — prix audio Mini dans la fiche fournisseur.
9. https://openrouter.ai/docs/guides/overview/multimodal/audio — chat audio, streaming et configuration.
10. https://ai.google.dev/gemini-api/docs/pricing — Google natif : Lyria Clip 0,04 $ / Pro 0,08 $ ; Gemini TTS et ratio 25 tokens/s.
11. https://ai.google.dev/gemini-api/docs/music-generation — Clip 30 s et compositions longues. Page actuelle orientée **Lyria 3.5** : ne pas transposer silencieusement durée/format/échantillonnage 3.5 au modèle 3 Pro Preview OR. La page pricing qualifie Lyria 3 de legacy, toujours listé sur OR à la consultation.

Les pages modèles OR demandées en markdown peuvent rediriger vers `llms.txt`, avec un exemple de chat générique qui n'est pas un guide musique suffisant. Les prix ci-dessus proviennent des catalogues, descriptions HTML tarifaires et de la tarification Google, pas du seul exemple générique.

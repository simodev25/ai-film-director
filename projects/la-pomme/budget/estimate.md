# Estimation avant scénario

**Estimation uniquement — aucune dépense autorisée.**

Projet : project_la_pomme · USD · tarifs vérifiés : 2026-10-05 · current_snapshot

## Hypothèses

- `duration_seconds` : 420
- `images` : 82
- `references_per_image` : 3
- `video_fraction` : 1.0
- `audio_seconds` : 60
- `text_input_tokens` : 100000
- `text_output_tokens` : 20000
- `attempts` : {'low': 1.0, 'mean': 1.25, 'high': 1.75}
- `contingency_fraction` : 0.1

Sources des tarifs :
- https://openrouter.ai/api/v1/models
- https://openrouter.ai/api/v1/images/models
- https://openrouter.ai/api/v1/videos/models
- https://openrouter.ai/docs/guides/overview/multimodal/tts.md

## Trois gammes — bas / moyen / haut

| Gamme | Images / vidéo | Bas | Moyen | Haut |
|---|---|---:|---:|---:|
| preparation | 1K / 720p | 15.6706 $ | 19.5882 $ | 27.4235 $ |
| tests | 1K / 720p | 52.7430 $ | 65.9287 $ | 92.3002 $ |
| production | 2K / 1080p | 105.4310 $ | 131.7887 $ | 184.5042 $ |

### preparation — détail moyen

Modèles : {'text': 'openai/gpt-6-luna', 'image': 'bytedance-seed/seedream-5-0-flash', 'video': 'google/veo-3.1-lite', 'audio': 'bytedance-seed/seed-audio-1-0'}

Vidéo par passe : 420 s facturables / 53 clips estimés.
- text_usd : 0.025000 $
- image_usd : 1.845000 $
- video_usd : 15.750000 $
- audio_usd : 0.187500 $
- subtotal_usd : 17.807500 $
- contingency_usd : 1.780750 $
- total_usd : 19.588250 $

### tests — détail moyen

Modèles : {'text': 'google/gemini-3.8-flash', 'image': 'google/gemini-3.1-flash-image', 'video': 'alibaba/wan-3.0', 'audio': 'bytedance-seed/seed-audio-1-0'}

Vidéo par passe : 420 s facturables / 14 clips estimés.
- text_usd : 0.187500 $
- image_usd : 7.060200 $
- video_usd : 52.500000 $
- audio_usd : 0.187500 $
- subtotal_usd : 59.935200 $
- contingency_usd : 5.993520 $
- total_usd : 65.928720 $

### production — détail moyen

Modèles : {'text': 'openai/gpt-6.1-sol', 'image': 'google/gemini-3-pro-image', 'video': 'google/veo-3.1', 'audio': 'bytedance-seed/seed-audio-1-0'}

Vidéo par passe : 420 s facturables / 53 clips estimés.
- text_usd : 0.500000 $
- image_usd : 14.120400 $
- video_usd : 105.000000 $
- audio_usd : 0.187500 $
- subtotal_usd : 119.807900 $
- contingency_usd : 11.980790 $
- total_usd : 131.788690 $

## Limites

- Estimation préliminaire, pas un devis, une facture ni une autorisation de dépense.
- Moyen = hypothèse de reprises choisie, pas une moyenne empirique ni une probabilité.
- Dimensions et tarifs correspondent aux réglages indiqués ; aucun changement de résolution automatique.
- Images et références Google : conversions estimatives des tokens ; texte/raisonnement image exclus.
- Budget texte limité aux tokens facturés spécifiés ; contexte GPT inférieur à 272000 tokens.
- Vidéo : arrondi des durées d'appels, hors limites réelles des shots et marges de raccord.
- Audio : secondes de sources générées, pas durée mixée ; sons réutilisables et silences ne sont pas des appels.
- Hors taxes, frais de crédits, licences, musique facultative, prises Foley, travail de montage/mixage.
- Pas de qualité ni de continuité garantie. Recalculer après le découpage et avant chaque lot payant.
- Sans fichier d'hypothèses : images = plafond(durée/8) images de plans + 12 illustrations de référence provisoires ; pas un découpage réel.

## Décision

Faire choisir la gamme et le plafond par l'utilisateur, puis enregistrer budget/decision.yaml avec le hash SHA-256 de estimate.yaml et la référence de son accord. Ne jamais créer un accord automatiquement. Cette revue autorise la planification du scénario, pas les appels cloud.

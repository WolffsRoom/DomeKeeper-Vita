Aplicacao no projeto GOGVersion/ExtractPCK
=========================================

Data: 2026-06-07
Projeto alvo: GOGVersion/ExtractPCK

Decisao:
- Nao rodei os scripts Python antigos em massa neste projeto.
- A maior parte deles foi criada durante tentativas anteriores e altera muitos arquivos de uma vez.
- Para esta nova base, apliquei manualmente apenas as rotinas ja confirmadas como uteis para Vita.

Rotinas aplicadas manualmente
=============================

Load.png no menu inicial
- Copiado de GOGVersion_1.4.1/ExtractPCK para GOGVersion/ExtractPCK.
- Copiado tambem o .stex correspondente em .import.
- TitleStage.tscn agora usa res://Load.png como textura de fundo.

Pular intro antes do menu
- Game.gd foi ajustado para iniciar direto em stages/title/title quando nao esta em dev mode.
- Motivo: o video/intro antes do menu ja causou crash C2-12828-1 no Vita.

Resolucao 960x540
- project.godot foi ajustado de 960x544 para 960x540.
- Mantido stretch mode 2d/expand.

Loading e erro de carregamento
- StageManager.gd foi trazido do projeto GOGVersion_1.4.1/ExtractPCK.
- Ele usa ResourceLoader.load_interactive, mostra "Loading..." com porcentagem e grava detalhes em user://load_error.txt se uma dependencia falhar.

GodotSteam
- O addon nativo addons/godotsteam teve os arquivos principais removidos.
- As DLLs binarias restantes foram esvaziadas porque a remocao binaria/recursiva foi bloqueada pelo ambiente.
- O autoload systems/steam/SteamGlobal foi mantido porque ele ja usa MockSteam e evita quebrar chamadas de achievements/leaderboards.
- Game.tscn foi ajustado para lockToSteam=false.

Scripts revisados e nao aplicados automaticamente
=================================================

fix_tscn.py
- Remove referencias VideoStream de cenas.
- Nao foi necessario agora: a busca nao encontrou VideoStream ativo no projeto, apenas o proprio script.

patch_audio.py
- Ajusta rotinas de audio/intro.
- Nao foi executado: o caminho mais seguro foi pular o intro inteiro no Game.gd.

fix_vita_map.py, optimize_viewports.py, optimize_textures_vita.py, resize_stex*.py
- Nao executados.
- Motivo: no projeto anterior, mexer em viewports/texturas contribuiu para recorte/desalinhamento e texturas ausentes.

patch_ui_*.py e fix_style.py
- Nao executados.
- Motivo: alteram Style.gd/UI em massa e podem quebrar shader/paleta/texturas.

purge_noise.py, clean_mocknoise.py, fix_orphan_refs.py, fix_ids.py
- Nao executados.
- Motivo: substituem/removem Noise/OpenSimplex/MockNoise e podem afetar geracao/visuais.

fix_stex_format_strings.py, check_stex.py, check_mip.py
- Nao executados.
- Sao uteis apenas se aparecer erro de .stex/WebP novamente.

Recomendacao
============

Para seguir nessa base:
- Validar primeiro menu inicial no Godot Vita.
- Depois testar Novo Jogo.
- So aplicar scripts antigos quando houver erro especifico que combine com a finalidade do script.

Inventario dos scripts Python encontrados
========================================

Data: 2026-06-07

Origem revisada:
- GOGVersion_1.4.1/PCK-Original
- GOGVersion_1.4.1/ExtractPCK

Observacao importante:
- O arquivo "s.py" nao foi encontrado em GOGVersion_1.4.1/PCK-Original nem em nenhuma pasta abaixo de Dome Keeper.v5.0.4.
- Os scripts Python encontrados estavam em GOGVersion_1.4.1/ExtractPCK. Foram copiados para esta pasta para arquivo e auditoria.
- Muitos scripts fazem alteracoes em massa no projeto. Nao execute novamente sem backup ou sem comparar com PCK-Original.

Resumo por script
=================

check_mip.py
- Uso provavel: diagnosticar cabecalhos de arquivos .stex em .import, imprimindo largura, altura, flags, mip_info, tipo e bytes extras.
- Categoria: diagnostico de textura.
- Risco: leitura apenas.

check_stex.py
- Uso provavel: comparar arquivos .stex bons/quebrados e confirmar se os bytes da imagem comecam em RIFF/WebP no offset esperado.
- Categoria: diagnostico de textura.
- Risco: leitura apenas, mas depende de nomes especificos de arquivos.

clean_mocknoise.py
- Uso provavel: remover referencias a MockNoise.gd e sub_resources orfaos de cenas/recursos.
- Categoria: limpeza de cenas/recursos.
- Risco: alto; altera varios .tscn/.tres.

compress_audio.py
- Uso provavel: mudar imports de WAV para compressao e taxa maxima de 22050 Hz, reduzindo memoria/tamanho para Vita.
- Categoria: otimizacao de audio.
- Risco: medio; altera .wav.import e pode reduzir qualidade.

fix_ids.py
- Uso provavel: corrigir IDs duplicados de ext_resource ligados a MockNoise.gd em .tscn/.tres.
- Categoria: correcao de recursos.
- Risco: medio; altera cenas/recursos que citam MockNoise.

fix_infinite_loop.py
- Uso provavel: ajustar export_presets.cfg e Data.gd para evitar loop/erro quando properties.yaml nao abre.
- Categoria: correcao de boot/export.
- Risco: alto; altera Data.gd e filtros de exportacao.

fix_map_casts.py
- Uso provavel: tentar forcar casts para PackedScene em loads de chambers dentro de Map.gd.
- Categoria: correcao de Map.gd.
- Risco: medio; pode gerar sintaxe ruim se combinado com .instance().

fix_map_preloads.py
- Uso provavel: trocar preloads do Map.gd por load/lazy load para evitar erros de preload no Godot Vita.
- Categoria: compatibilidade Godot Vita.
- Risco: alto; altera preloads e fluxo de _ready().

fix_mapgd.py
- Uso provavel: corrigir sintaxe em Map.gd, principalmente arrays multiline, chaves negativas e uso incorreto de tileData().
- Categoria: correcao de parser.
- Risco: medio; altera trechos especificos de Map.gd.

fix_map_casts.py
- Uso provavel: adicionar "as PackedScene" em loads de cenas de chamber.
- Categoria: tentativa de tipagem.
- Risco: medio; pode nao ser necessario no estado atual.

fix_map_preloads.py
- Uso provavel: converter preloads de Map.gd para loads em tempo de execucao.
- Categoria: compatibilidade com carregamento no Vita.
- Risco: alto; pode mascarar recurso quebrado.

fix_orphan_refs.py
- Uso provavel: substituir arquivos .tres de noise por Resource vazio e remover script ExtResource orfao.
- Categoria: limpeza de referencias quebradas.
- Risco: alto; remove comportamento de noise se usado.

fix_stex_format_strings.py
- Uso provavel: remover string de formato "WEBP"/"PNG " embutida no payload de .stex e ajustar tamanho do dado.
- Categoria: correcao de textura .stex.
- Risco: alto; altera binarios .stex.

fix_style.py
- Uso provavel: reescrever Style.gd para aplicar paleta/estilo sem quebrar grupos styled/unstyled.
- Categoria: correcao visual/Style.gd.
- Risco: alto; substitui bloco grande de logica visual.

fix_syntax.py
- Uso provavel: corrigir ocorrencias invalidas de "as PackedScene.instance()" em Map.gd.
- Categoria: correcao de parser.
- Risco: baixo/medio; substituicao simples.

fix_tres.py
- Uso provavel: mover "script = ExtResource(...)" para dentro do bloco [resource] em .tres.
- Categoria: correcao de recursos.
- Risco: medio; altera .tres em massa.

fix_tscn.py
- Uso provavel: remover VideoStream e referencias de stream de cenas .tscn, provavelmente para evitar codecs/recursos nao suportados.
- Categoria: compatibilidade/limpeza de cenas.
- Risco: alto; remove videos/cutscenes.

fix_viewport_textures.py
- Uso provavel: corrigir ViewportTexture/Viewport em Map.tscn para tentar restaurar renderizacao do mapa.
- Categoria: correcao visual do mapa.
- Risco: alto; altera estrutura sensivel de Map.tscn.

fix_vita_map.py
- Uso provavel: patch grande para adaptar Map.tscn/Map.gd ao Vita, incluindo viewport, texturas e shaders.
- Categoria: compatibilidade visual do mapa.
- Risco: muito alto; deve ser tratado como tentativa historica, nao como script seguro.

optimize_imports.py
- Uso provavel: alterar arquivos .import para reduzir tamanho/memoria, provavelmente limites de textura/filtros/mipmaps.
- Categoria: otimizacao de importacao.
- Risco: medio/alto; pode afetar qualidade e atlas.

optimize_textures_vita.py
- Uso provavel: otimizar imports/texturas para Vita, reduzindo consumo de memoria.
- Categoria: otimizacao de textura.
- Risco: alto; pode quebrar atlas/sprites se reduzir imagens erradas.

optimize_viewports.py
- Uso provavel: reduzir tamanhos de Viewport em cenas para tentar caber na memoria do Vita.
- Categoria: otimizacao de viewport.
- Risco: alto; foi uma provavel causa de desalinhamento/recorte visual.

patch_audio.py
- Uso provavel: alterar configuracoes de audio/imports para compatibilidade ou memoria no Vita.
- Categoria: audio.
- Risco: medio; pode alterar qualidade/carregamento.

patch_eol.py
- Uso provavel: corrigir fim de linha/encoding em arquivos, provavelmente para parser do Godot.
- Categoria: encoding/EOL.
- Risco: baixo/medio; pode gerar mudancas grandes sem efeito funcional.

patch_eol2.py
- Uso provavel: segunda tentativa de corrigir fim de linha/encoding.
- Categoria: encoding/EOL.
- Risco: baixo/medio.

patch_error_report.py
- Uso provavel: adicionar ou ajustar rotina de relatorio de erro/carregamento.
- Categoria: diagnostico runtime.
- Risco: medio; altera fluxo de erro.

patch_error_report_file.py
- Uso provavel: gravar erro em arquivo para depuracao no Vita.
- Categoria: diagnostico runtime.
- Risco: medio; altera StageManager/fluxo de erro.

patch_error_report_file2.py
- Uso provavel: segunda variante para gravar erro em arquivo.
- Categoria: diagnostico runtime.
- Risco: medio.

patch_fade.py
- Uso provavel: ajustar/remover fade visual ou shader de transicao.
- Categoria: UI/transicao.
- Risco: medio; pode afetar telas de loading/transicao.

patch_interactive.py
- Uso provavel: adicionar tratamento interativo/erro de loading para conseguir continuar quando cenas falham.
- Categoria: diagnostico e fluxo de cena.
- Risco: alto; pode esconder falhas reais.

patch_interactive_fix.py
- Uso provavel: corrigir a tentativa anterior de patch_interactive.py.
- Categoria: diagnostico e fluxo de cena.
- Risco: alto.

patch_labels.py
- Uso provavel: ajustar labels/textos de loading ou UI.
- Categoria: UI.
- Risco: baixo/medio.

patch_label_center.py
- Uso provavel: centralizar label de loading/erro.
- Categoria: UI.
- Risco: baixo.

patch_label_font.py
- Uso provavel: ajustar fonte/escala de label de loading/erro.
- Categoria: UI.
- Risco: baixo.

patch_loading_anim.py
- Uso provavel: alterar animacao/tela de carregamento para o Vita.
- Categoria: UI/loading.
- Risco: medio.

patch_null_report.py
- Uso provavel: adicionar relatorio quando uma cena/recurso retorna null.
- Categoria: diagnostico runtime.
- Risco: medio.

patch_percent.py
- Uso provavel: ajustar exibicao de percentual/progresso de loading.
- Categoria: UI/loading.
- Risco: baixo/medio.

patch_polls.py
- Uso provavel: ajustar quantidade/frequencia de polls no carregamento.
- Categoria: loading/performance.
- Risco: medio.

patch_recursive.py
- Uso provavel: patch recursivo em StageManager ou carregamento para tentar resolver dependencia/cena.
- Categoria: fluxo de cena.
- Risco: alto.

patch_stage.py
- Uso provavel: modificar StageManager.gd para mostrar "Loading... / Carregando..." e aguardar frames ao trocar stages.
- Categoria: UI/loading e troca de cena.
- Risco: alto; altera fluxo central de stages.

patch_ui_back.py
- Uso provavel: recolocar shader/material em controles de UI via Style.gd.
- Categoria: UI/Style.gd.
- Risco: alto; pode quebrar cores/texturas.

patch_ui_remove.py
- Uso provavel: remover aplicacao de shader em controles de UI.
- Categoria: UI/Style.gd.
- Risco: alto; tentativa oposta a patch_ui_back.py.

patch_ui_shader_again.py
- Uso provavel: restaurar shader em controles de UI depois de remocao.
- Categoria: UI/Style.gd.
- Risco: alto; conflito com outros patch_ui_*.

patch_ui_style.py
- Uso provavel: adicionar controles de UI ao tratamento de Style.gd.
- Categoria: UI/Style.gd.
- Risco: alto.

patch_ui_tint.py
- Uso provavel: trocar shader de UI por self_modulate/tint.
- Categoria: UI/Style.gd.
- Risco: alto; pode causar cores erradas.

patch_ui_tint2.py
- Uso provavel: trocar shader de UI por modulate/tint.
- Categoria: UI/Style.gd.
- Risco: alto; variante de patch_ui_tint.py.

patch_user_path.py
- Uso provavel: trocar caminho de log de "ux0:load_error.txt" para "user://load_error.txt".
- Categoria: diagnostico Vita.
- Risco: baixo; muda destino do arquivo de log.

purge_noise.py
- Uso provavel: substituir OpenSimplexNoise/NoiseTexture por Resource/MockNoise para contornar incompatibilidade.
- Categoria: compatibilidade de noise.
- Risco: muito alto; pode afetar geracao de mapa e visuals.

remove_empty_textures.py
- Uso provavel: remover ImageTexture vazias e parametros relacionados em Map.tscn.
- Categoria: correcao visual do mapa.
- Risco: alto; pode remover referencias necessarias.

rename_refs.py
- Uso provavel: trocar referencias de HighlightShader.material para HighlightShader.tres.
- Categoria: correcao de paths.
- Risco: baixo/medio; altera referencias em massa.

resize_stex.py
- Uso provavel: reduzir .stex grandes para 512, evitando sprite sheets, para caber na memoria do Vita.
- Categoria: otimizacao de textura .stex.
- Risco: alto; primeira versao assumia cabecalho com string de formato.

resize_stex_v2.py
- Uso provavel: segunda versao do redimensionador .stex, aceitando cabecalho de 28 ou 32 bytes.
- Categoria: otimizacao de textura .stex.
- Risco: alto; pode quebrar atlas se classificar errado.

restore_atlas_stex.py
- Uso provavel: restaurar .stex usados como AtlasTexture a partir dos PNGs originais.
- Categoria: recuperacao de textura/atlas.
- Risco: medio/alto; tenta desfazer resize errado.

restore_atlas_stex_v2.py
- Uso provavel: segunda versao para restaurar atlas respeitando dimensoes do import do Godot.
- Categoria: recuperacao de textura/atlas.
- Risco: medio/alto; mais correta que restore_atlas_stex.py.

strip_bom.py
- Uso provavel: remover BOM UTF-8 de .tscn, .tres e .gd.
- Categoria: encoding.
- Risco: baixo/medio; altera muitos arquivos, mas geralmente seguro.

write_utf8.py
- Uso provavel: recriar HighlightShader.material em UTF-8 puro sem BOM.
- Categoria: encoding/correcao de material.
- Risco: baixo/medio; sobrescreve um arquivo especifico.

Recomendacao
============

Para seguir com o port:
- Use PCK-Original como referencia limpa.
- Evite rodar scripts patch_ui_*, optimize_viewports.py, purge_noise.py, fix_vita_map.py e resize_stex*.py sem backup.
- Scripts de diagnostico como check_mip.py e check_stex.py sao seguros para leitura.
- Para novas correcoes, prefira patches pequenos e documentados em vez de scripts de alteracao em massa.

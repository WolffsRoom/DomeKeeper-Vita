# scripts/ — Ferramentas do port Dome Keeper PSVita

Scripts de desenvolvimento/empacotamento. **Não fazem parte do jogo** — operam sobre
`GOGVersion/VitaBuild` (caminhos absolutos embutidos em cada script). O jogo em si fica em
`GOGVersion/VitaBuild`; a versão de teste PC fica em `GOGVersion/OriginalPCK`.

## Layout

```
scripts/
  stex/        formato/inspeção das texturas .stex (StreamTexture)
    revert_all_stex.py    Converte .stex da variante B (quebrada) -> A (correta). FIX OFICIAL.
    scan_stex_format.py   Relatório do formato WebP de cada .stex (A correto / B quebrado).
    check_stex.py, check_mip.py   Inspeção pontual de header/mipmaps.
  textures/    redimensionamento/otimização de imagens p/ limites do Vita (4096px, etc.)
    scan_textures_vita.py, optimize_vita.py, resize_stex_v2.py, restore_atlas_stex_v2.py
  shaders/
    fix_shaders_vita.py   Aplica o fix _suv (SCREEN_UV -> variável local) nos shaders.
  validate/
    validate_vitabuild.py  Validação geral antes de gerar o PCK.
    validate_refs.py        Checa referências res:// quebradas.
  restore/     restauração de recursos a partir do PCK original
    restore_all_from_original.py, restore_all_missing.py
  audio/       compressão/patch de áudio (WAV -> IMA-ADPCM, etc.)
    compress_audio.py, patch_audio.py
  _history/    one-offs já aplicados e dumps antigos (referência; não precisam rodar de novo)
    tools_scritps/                  patches pontuais da fase de bring-up
    combined_scripts_fb1d.py        blob concatenado original (contém TUDO acima, sujo)
    combined_shaders_revert_3946.py blob concatenado original (shaders + revert)
    texture_report.txt              relatório gerado antigo
```

## AVISOS (ver memória do projeto)

1. **Formato .stex**: o correto é `WEBP` seguido **direto** de `RIFF` (variante A) — vale para
   PC **e** para o fork `Tools/Godot_v3.5-rc5-vita.exe`. O `Details.txt` #1 está errado ao dizer
   que o Vita precisa de um prefixo diferente.
2. **NUNCA rodar um `fix_all_stex`** (a lógica antiga existe só dentro de
   `_history/combined_scripts_fb1d.py`). Ela insere um u32 entre `WEBP` e `RIFF` (variante B) e
   gera `Error unpacking WEBP image`. Para consertar, use `stex/revert_all_stex.py`.
3. **Shaders `SCREEN_TEXTURE` + luz 2D** travam a compilação na GPU do Vita. Remédio:
   `render_mode unshaded;` no shader (quando o efeito não precisa reagir à luz).

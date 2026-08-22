#  Bot de Economía Discord.py

- **Comandos Slash** y con **prefijo** configurable.
- **Economía** compartida mediante un único `economy.json`.
- Sistema de **Staff** con roles configurables.
- Juegos interactivos (robo, ruleta).
- Perfiles de usuario y ranking.
- Sistema de ayuda y manejo de errores.

###  Economía
- Guardada en `datos/economy.json` (bolsillo, banco, cooldowns, estadísticas)
- El dinero del banco está protegido contra robos.
- Staff y juegos totalmente configurables.


**Staff** solo puede usar los roles configurados, con confirmación interactiva para acciones destructivas (`/resetear`, `/quitar`), y cada acción se registra en `datos/registros_staff.json` y se envía al canal de registros.

###  Ejecución
```bash
pip install -r requirements.txt
python src/bot.py
```

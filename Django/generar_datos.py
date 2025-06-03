import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Parámetros de generación de datos
num_entregas = 50000  # Total de registros deseados
fecha_inicio = datetime(2020, 1, 1)  # Fecha inicial de los datos
productores = [1, 2, 3, 4, 5, 6, 7]  # IDs de productores
usuarios = [1]  # ID del usuario

# Generar datos aleatorios
data = []
fecha_actual = fecha_inicio
entregas_generadas = 0

while entregas_generadas < num_entregas:
    num_entregas_dia = np.random.randint(30, 46)  # Entre 30 y 45 entregas por día
    for _ in range(num_entregas_dia):
        if entregas_generadas >= num_entregas:
            break
        cantidad = round(np.random.uniform(0.01, 20.00), 2)  # Cantidad entre 0.01 y 20.00
        productor_id = np.random.choice(productores)
        usuario_id = np.random.choice(usuarios)
        data.append([fecha_actual.strftime("%Y-%m-%d"), cantidad, productor_id, usuario_id])
        entregas_generadas += 1
    fecha_actual += timedelta(days=1)

# Crear DataFrame y guardar en CSV
df = pd.DataFrame(data, columns=["fecha", "cantidad", "productor_id", "usuario_id"])
df.to_csv("entregas_historicas.csv", index=False)

print(f"✅ Archivo 'entregas_historicas.csv' generado con {len(df)} registros.")

### Actualizar codigo en la maquina virtual
1.Actualizar y Subir el Contenedor
Cada vez que hagas un cambio, es recomendable usar una "etiqueta" (tag) nueva (como :v2, :v3, etc.) para llevar un control.

### Paso A: Construir la nueva versión
Ejecuta esto en la carpeta de tu proyecto en tu Mac:
````
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v2 .
Paso B: Subirla al repositorio de Google
```
```
docker push us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v2
Paso C: Actualizar la Máquina Virtual
Este comando le indica a tu instancia bot-visas-vm que descargue la nueva imagen y reinicie el contenedor con ella
```
gcloud compute instances update-container bot-visas-vm \
  --zone=us-central1-a \
  --container-image=us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v12
  ```
2.Ver los Logs en la Máquina Virtual
Paso A: Conectarte a la VM
```
gcloud compute ssh bot-visas-vm --zone=us-central1-a

kevin@bot-visas-vm ~ $ docker rm -f caddy-proxy
caddy-proxy
kevin@bot-visas-vm ~ $ docker run -d --name caddy-proxy \
-p 80:80 -p 443:443 \
-v caddy_data:/data \
caddy caddy reverse-proxy \
--from https://api.puntovisas.com \
--to 34.29.125.129:8080




------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Aquí tienes una guía completa estructurada como un `README.md` para que puedas gestionar tu infraestructura de Google Cloud (GCP) con Docker y Caddy de forma profesional.

---

# 🚀 Guía de Despliegue: Bot Visas API

Este documento detalla los pasos para desplegar, actualizar y configurar la infraestructura de la API en Google Compute Engine (VM) utilizando Docker y Caddy como Reverse Proxy con SSL automático.

## 📌 1. Configuración de IP Estática (Fija)
Para que tu dominio siempre apunte a la misma máquina, necesitas que la IP externa no cambie al reiniciar la VM.

1.  **Desde tu terminal local (Mac):**
    ```bash
    # Reserva una IP estática regional
    gcloud compute addresses create bot-visas-ip \
        --region=us-central1
    ```
2.  **Asociar la IP a tu VM existente:**
    ```bash
    # Primero obtenemos el nombre de la configuración de acceso actual (usualmente 'external-nat')
    # Luego la asociamos (reemplaza [IP_RESERVADA] con la que te dio el comando anterior)
    gcloud compute instances add-access-config bot-visas-vm \
        --zone=us-central1-a \
        --address=[IP_RESERVADA]
    ```
    *Nota: También puedes hacerlo en la consola de GCP: Red de VPC -> Direcciones IP -> Cambiar tipo de "Efímera" a "Estática".*

---

## 🏗 2. Creación y Despliegue del Contenedor (VM)

### Paso A: Construir y subir la imagen (Desde tu Mac)
Cada vez que hagas cambios en el código, incrementa la versión (`v1`, `v2`, etc.).

```bash
# 1. Construir la imagen para arquitectura Linux (importante para VMs de Google)
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v6 .

# 2. Subir al Artifact Registry
docker push us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v6
```

### Paso B: Actualizar la VM con la nueva versión
Este comando detiene el contenedor anterior y levanta el nuevo automáticamente.

```bash
gcloud compute instances update-container bot-visas-vm \
  --zone=us-central1-a \
  --container-image=us-central1-docker.pkg.dev/project-ef8e5f6d-c593-40a2-b0b/cloud-run-source-deploy/mi-api-flask:v8
```

---

## 🌐 3. Configuración del Dominio y SSL (Caddy)

Caddy se encarga de recibir el tráfico en los puertos **80** (HTTP) y **443** (HTTPS) y redirigirlo internamente a tu contenedor que corre en el **8080**.

### Comando para el Proxy Inverso
Entra a tu VM vía SSH y ejecuta:

gcloud compute ssh bot-visas-vm --zone=us-central1-a

```bash
# 1. Eliminar cualquier versión anterior de caddy para evitar conflictos
docker rm -f caddy-proxy

# 2. Ejecutar Caddy con redireccionamiento a tu IP y Puerto
# IMPORTANTE: Cambia [TU_IP_ESTATICA] por la IP que fijamos en el punto 1
docker run -d --name caddy-proxy \
  -p 80:80 -p 443:443 \
  -v caddy_data:/data \
  caddy caddy reverse-proxy \
  --from https://api.puntovisas.com \
  --to [TU_IP_ESTATICA]:8080
```

---

## 🛠 4. Comandos de Mantenimiento (SSH)

Una vez dentro de la VM (`gcloud compute ssh bot-visas-vm`), usa estos comandos para monitorear:

| Acción | Comando |
| :--- | :--- |
| **Ver logs de la API** | `docker logs -f klt-bot-visas-vm-swqc` |
| **Ver logs de Caddy** | `docker logs -f caddy-proxy` |
| **Listar contenedores** | `docker ps` |
| **Reiniciar Proxy** | `docker restart caddy-proxy` |

---

## 📋 Resumen de Flujo de Trabajo
1.  **Modificas código** en tu MacBook.
2.  **Build & Push** de la imagen con una nueva etiqueta (ej. `:v7`).
3.  **Update-container** en la VM usando `gcloud`.
4.  **Caddy** detectará que el servicio interno volvió a subir y seguirá sirviendo bajo `https://api.puntovisas.com`.

> [!TIP]
> Asegúrate de que en el panel de Google Cloud, el **Firewall** tenga permitidos los puertos **80** y **443** para tráfico externo, de lo contrario, el dominio nunca llegará a la VM.
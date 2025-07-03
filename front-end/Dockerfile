FROM nginx:1.25-alpine

# Copiar el build (lo que generó Vite)
COPY dist/ /usr/share/nginx/html/

# Opcional: reemplazar configuración por defecto
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

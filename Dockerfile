FROM nginx:alpine

ARG GIT_COMMIT=unknown

# Commit als Klartext unter / und /commit ausliefern
RUN printf '%s' "$GIT_COMMIT" > /usr/share/nginx/html/index.html \
 && printf '%s' "$GIT_COMMIT" > /usr/share/nginx/html/commit

EXPOSE 80

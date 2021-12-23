import os
from pathlib import Path

CMD_1 = """
touch ~/example.log
cat >~/example.conf <<EOF
server {
  listen 80;
  server_name localhost;
  access_log /var/log/nginx/custom.host.access.log main;
  location / {
    root /usr/share/nginx/html;
    index index.html index.htm;
  }
}
EOF
"""

# definir un lien entre le containeur et syteme fichier hote (src : source fichier hote, dst :  destination ficher contenaineur)
CMD_2 = """
CONF_SRC=~/exemple.conf ; \
CONF_DST=/etc/nginx/conf.d/default.conf ; \

LOG_SRC=~/exemple.log ; \
LOG_DST=/var/log/nginx/custom.host.access.log ; \
docker run -d --name diaweb \
  --mount type=bind,src=${CONF_SRC},dst=${CONF_DST} \
  --mount type=bind,src=${LOG_SRC},dst=${LOG_DST} \
  -p 80:80 \
  nginx:dernier
"""

# read only (empeche corrumption fichier par le containeur)
CMD_3= """
CONF_SRC=~/example.conf; \
CONF_DST=/etc/nginx/conf.d/default.conf; \
LOG_SRC=~/example.log; \
LOG_DST=/var/log/nginx/custom.host.access.log; \
docker run -d --name diaweb \
  --mount type=bind,src=${CONF_SRC},dst=${CONF_DST},readonly=true \
  --mount type=bind,src=${LOG_SRC},dst=${LOG_DST} \
  -p 80:80 \
  nginx:latest
"""

#mémoire tampon(utilisation puis suppresion) pour fichier ou objet sensible
CMD_4 = """
docker run --rm \
--mount type=tmpfs,dst=/tmp \
--entrypoint mount \
alpine:latest -v
"""

#tmps avec limitation
CMD_5 = """
docker run --rm \
--mount type=tmpfs,dst=/tmp,tmpfs-size=16k,tmpfs-mode=1770 \
--entrypoint mount \
alpine:latest -v
"""

CMD_6 = """
docker volume create \
--driver local \
--label example=location \
location-example 
& docker volume inspect \
--format "{{json .Mountpoint}}" \
location-example
"""

#creation de volume partagée => accessible au conteneurs
CMD_7 = """
docker volume create \
    --driver local \
    --label example=cassandra \
    cass-shared
"""

#Utilisation du volume cass-shared par un conteneur
CMD_7 = """
docker run -d \
  --volume cass-shared:/var/lib/cassandra/data \
    --name cass1 \
      cassandra:2.2
      """

## execution du containeur en mode interative (-it) et suppression par la suite (--rm)
CMD_8 = """
docker run -it --rm \
  --link cass1:cass \
      cassandra:2.2 cqlsh cass
"""

#suppresion du docker
CMD_9 =  """
docker stop cass1
docker rm -vf cass1
"""

#Lien entre deux conteneur (faiblesse : définir un emplacement & possibilité de conflit entre les conteneur)
CMD_10 = """
LOG_SRC=~/web-logs-example
mkdir ${LOG_SRC}      

docker run --name plath -d \
  --mount type=bind,src=${LOG_SRC},dst=/data \
    dockerinaction/ch4_writer_a                     
&
docker run --rm \
    --mount type=bind,src=${LOG_SRC},dst=/data \
      alpine:latest \
        head /data/logA                                 
&       
cat ${LOG_SRC}/logA
&
docker rm -f plath                               
"""

#Commande equivalente avec volume 
# (avantage : pas à se mettre d'accord sur l'emplacement de manière explicite)
CMD_11 = """
docker volume create \
  --driver local \
      logging-example                                         

docker run --name plath -d \
  --mount type=volume,src=logging-example,dst=/data \
      dockerinaction/ch4_writer_a                             

docker run --rm \
    --mount type=volume,src=logging-example,dst=/data \
      alpine:latest \
      head /data/logA                                         

cat "$(docker volume inspect \
    --format "{{json .Mountpoint}}" logging-example)"/logA

docker stop plath
"""



if __name__ == "__main__":
    os.system(f"sudo {CMD_1}")

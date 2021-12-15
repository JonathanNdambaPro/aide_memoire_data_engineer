import os

# lance en arriere plan l'app et nomme web
CMD_1 = "docker run --detach \
    --name web nginx:latest"

# ' --interactive indique à Docker de garder le flux d'entrée standard (stdin) ouvert pour le conteneur même si aucun terminal n'est connecté.
#  --tty indique à Docker d'allouer un terminal virtuel au conteneur, ce qui vous permettra de transmettre des signaux au conteneur
CMD_2 = "docker run --interactive --tty \
    --link web:web \
        --name web_test \
            busybox:1.29 /bin/sh"

CMD_3 = "docker run -it \
    --name agent \
        --link web:insideweb \
            --link mailer:insidemailer \
                dockerinaction/ch2_agent"

# liste les conteneurs en cours d'execution
# L'identifiant du conteneur
# L'image utilisée
# La commande exécutée dans le conteneur
# Le temps écoulé depuis la création du conteneur
# La durée d'exécution du conteneur
# Les ports réseau exposés par le conteneur
# Le nom du conteneur
CMD_4 = "docker ps -a"


#demarrer un conteneur arrete
CMD_5 = "docker start web"

#redemarrer un conteneur arrete
CMD_6 = "docker restart web"

#afficher les logs des app dans un conteneur (stdout or stderr)
CMD_7 = "docker logs web"

CMD_8 = """docker run -d --name namespaceA busybox:1.29 /bin/sh -c 'sleep 30000' \
    docker run -d --name namespaceB busybox:1.29 /bin/sh -c "nc -l 0.0.0.0 -p 80"""

#To clean the docker environment, removing all the containers and images.
CMD_9 = """docker system prune -a"""

# TODO: docker ps -a: To see all the running containers in your machine.
# TODO: docker stop <container_id>: To stop a running container.
# TODO: docker rm <container_id>: To remove/delete a docker container(only if it stopped).
# TODO: docker image ls: To see the list of all the available images with their tag, image id, creation time and size.
# TODO: docker rmi <image_id>: To delete a specific image.
# TODO: docker rmi -f <image_id>: To delete a docker image forcefully
# TODO: docker rm -f (docker ps -a | awk '{print$1}'): To delete all the docker container available in your machine
# TODO: docker image rm <image_name>: To delete a specific im

# docker exec command to run additional processes in a running container. In this case, the command you use is called ps, which shows all the running processes and their PID
CMD_10 = """ docker exec namespaceA ps &\
    docker exec namespaceB ps"""


#Stocker l'id de l'mqge dans une variale d'environement dans la variale 
CMD_11 = """MAILER_CID=$(docker run -d dockerinaction/ch2_mailer)
WEB_CID=$(docker create nginx)

AGENT_CID=$(docker create --link $WEB_CID:insideweb \
    --link $MAILER_CID:insidemailer \
    dockerinaction/ch2_agent)"""
    
#Lecture e fichier seul
CMD_12 = """docker run -d --name wp --read-only \
    wordpress:5.0.0-php7.2-apache"""


#injection de variable d'environement dans le docker puis (Derniere ligne) execution
CMD_13 = """docker run --env MY_ENVIRONMENT_VAR="ceci est un test" \
    busybox:1.29 \
        env"""

def cmd_docker(cmd): os.system(cmd)


if __name__ == "__main__":
    cmd_docker(CMD_10)
 
                         
 

 
                          

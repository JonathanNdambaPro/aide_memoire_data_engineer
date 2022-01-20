import os

#Creation de reseau docker
CMD_1 = """
docker network create \
  --driver bridge \
  --label project=dockerinaction \
  --label chapter=5 \
  --attachable \
  --scope local \
  --subnet 10.0.42.0/24 \
  --ip-range 10.0.42.128/25 \
  user-network 
"""

#associer un dockeur au reseau et inspecter son ip
CMD_2 = """
docker run -it \
  --network user-network \
  --name network-explorer \
  alpine:3.8 \
    sh 
ip -f inet -4 -o addr
"""
#création d'un second reseau et connection au premier par un bridge
CMD_3 = """
docker network create \
  --driver bridge \
  --label project=dockerinaction \
  --label chapter=5 \
  --attachable \
  --scope local \
  --subnet 10.0.43.0/24 \
  --ip-range 10.0.43.128/25 \
  user-network2
  
  docker network connect \
  user-network2 \
  network-explorer
  """
if __name__ == "__main__":
    os.system(f"sudo {CMD_3}")

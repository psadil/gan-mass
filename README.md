
Many of the steps outlined below use Google products that are not free. Make sure to monitor your costs. 

## Network

For an architecture, I used [stylegan2-ada](https://github.com/NVlabs/stylegan2-ada). They detail a few ways to work with their network and tools. The network was built using an older version of Tensforflow (a 1.x version), but Nvidia helpfully provides a docker image containing the network and utility tools. 

```
docker build --tag stylegan2ada:latest libs/stylegan2-ada
```

## Data

### Acquire Images

To download images from the Static Street View API, see `downloads.py`. The script is not terribly convenient. It relies on manually changing the variable `data`, including origin, destination, and potentially waypoints. See the [Directions API](https://developers.google.com/maps/documentation/directions/overview) for details. 

To use the Google APIs, you will need an API key. The code in this repository (e.g., `downloads.py`) will work if your key is assigned to a variable called `GOOGLE` in a file called `secrets.py`, e.g.,

```bash
# in bash
echo "GOOGLE = 'YOUR_API_KEY'" > secrets.py
```

### Clean Images

The images will be downloaded as 640x460 jpg files. That's an awkward size, not being a power of 2. Use the commandline funtion defined in `shrink_images.py` to reduce them to 512x512.

```bash
python shrink_images.py "data-raw/**/*jpg" data/mass512
```

### Create Rectord

Finally, the stylegan2-ada architecture works with [tensorflow records](https://www.tensorflow.org/tutorials/load_data/tfrecord). But the docker image created above comes with a function for converting the data. Here's an example of the command.

```bash
docker run -it --rm -v `pwd`:/scratch --user $(id -u):$(id -g) \
  stylegan2ada:latest bash -c "(python /scratch/libs/stylegan2-ada/dataset_tool.py  \
  create_from_images /scratch/data/mass512record /scratch/data/mass512)"
```

## Training

I trained the networks on a [preemptible VM](https://cloud.google.com/preemptible-vms/) with the following configuration

- Machine type: n1-highmem-4 (4 vCPUs, 26 GB memory)
- Zone: us-central1-a
- GPU: one V100
- boot disk:  Intel® optimized Deep Learning Image: TensorFlow 1.15 m59 (with Intel® MKL-DNN/MKL and CUDA 110)

I only trained the final network for 24 hours. The final cost was under $50, well under the $300 credits they allot for signing up.

## Generate Images from Trained Network

Again, thanks to the stylegan2-ada repository for providing a script that automates generating images. The following will produce 100 samples from a snapshot of the network.  

```
python stylegan2-ada/generate.py \
  --outdir=outdir 
  --seeds=0-99 \
  --network=training/00000-mass512-auto1/network-snapshot-001000.pkl
```
echo "Enter Model Name:"
read modelName
echo "Downloading Model: $modelName"

# Clone HF Repo
git clone https://huggingface.co/openai/whisper-$modelName
# Go to the directory
cd whisper-$modelName/
# Remove unnecessary files
rm -r .git .gitattributes .gitignore *.h5 *.safetensors *.msgpack *.bin
# Download pytorch model
wget https://huggingface.co/openai/whisper-$modelName/resolve/main/pytorch_model.bin
# Go back to the main directory
cd ..
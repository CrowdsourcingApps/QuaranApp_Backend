# How to upload data to a dataset

1. Run the script _**export_data_to_dataset.py**_
2. Copy resulting _**temp_audio_chunks**_ dir and _**metadata.jsonl**_ file to a separate directory
3. cd to the directory and run
`huggingface-cli upload quran-recitation-errors-test . . --repo-type dataset --commit-message="Your commit message"`


SHDW_API_ENDPOINT = "https://shadow-storage.genesysgo.net"

async def shdwUpload(
    file: str,
    storageAccount="5mojD7z7wyVAYG8ncnYcr2en3cYU1pKXkcZfEQovW8d5",
    keypair=None,
):
    storageAccount = PublicKey(storageAccount)

    async with aiofiles.open(file, "rb") as f:
        data = await f.read()
    # allfileNames = [f.name]
    # create sha256 hash for the file
    fileHashSum = hashlib.sha256()
    fileNameHashSum = hashlib.sha256()
    fileHashSum.update(data)
    fileNameHashSum.update(f.name.encode())
    fileHash = fileHashSum.hexdigest()
    fileNameHash = fileNameHashSum.hexdigest()

    msg = f"Shadow Drive Signed Message:\nStorage Account: {storageAccount.to_base58()}\nUpload files with hash: {fileNameHash}"
    # create a variable called msgSig which is a Uint8Array
    msgSig = SigningKey(keypair.seed).sign(msg.encode())
    encodedMsg = msgSig.signature

    verify = SigningKey(keypair.seed).verify_key.verify(
        msgSig.message, msgSig.signature
    )

    fd = FormData()
    fd.add_field("file", data, filename=f.name)
    fd.add_field("fileNames", f.name)
    fd.add_field("message", b58encode(encodedMsg))
    fd.add_field("storage_account", storageAccount.to_base58())
    fd.add_field("signer", str(keypair.public_key))

    async with ClientSession() as session:
        async with session.post(f"{SHDW_API_ENDPOINT}/upload", data=fd) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

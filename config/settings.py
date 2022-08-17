import os

import dotenv

dotenv.load_dotenv()


class Settings:
    # Server
    GRPC_VERBOSITY = os.getenv("GRPC_VERBOSITY")
    GRPC_TRACE = os.getenv("GRPC_TRACE")
    GRPC_HOST = os.getenv("GRPC_HOST", "0.0.0.0")
    GRPC_PORT = os.getenv("GRPC_PORT", "50041")

    # Comunication
    CF_HOST = os.getenv("CF_HOST")
    CF_PORT = os.getenv("CF_PORT")
    GIS_HOST = os.getenv("GIS_HOST")
    GIS_PORT = os.getenv("GIS_PORT")
    TEO_HOST = os.getenv("TEO_HOST")
    TEO_PORT = os.getenv("TEO_PORT")
    MM_HOST = os.getenv("MM_HOST")
    MM_PORT = os.getenv("MM_PORT")
    BM_HOST = os.getenv("BM_HOST")
    BM_PORT = os.getenv("BM_PORT")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

from __future__ import annotations

import dataclasses
from os.path import split
from typing import Optional, List
from typing_extensions import TypedDict, NotRequired


@dataclasses.dataclass
class CivitFile:
    """
    A file on CivitAI

    Attributes:
        model_id (int): The ID of the model
        model_version_id (int): The version
        filename (str): The name of the file in the model
    """
    model_id: int
    model_version_id: int
    filename: str

    def __str__(self):
        return self.filename

    @property
    def save_with_filename(self):
        return self.filename

    @property
    def alternate_filenames(self):
        return []


@dataclasses.dataclass
class HuggingFile:
    """
    A file on Huggingface Hub

    Attributes:
        repo_id (str): The Huggingface repository of a known file
        filename (str): The path to the known file in the repository
        show_in_ui (bool): Not used. Will indicate whether or not the file should be shown in the UI to reduce clutter
    """
    repo_id: str
    filename: str
    save_with_filename: Optional[str] = None
    alternate_filenames: List[str] = dataclasses.field(default_factory=list)
    show_in_ui: Optional[bool] = True

    def __str__(self):
        return split(self.filename)[-1]


class CivitStats(TypedDict):
    downloadCount: int
    favoriteCount: NotRequired[int]
    thumbsUpCount: int
    thumbsDownCount: int
    commentCount: int
    ratingCount: int
    rating: float
    tippedAmountCount: NotRequired[int]


class CivitCreator(TypedDict):
    username: str
    image: str


class CivitFileMetadata(TypedDict, total=False):
    fp: Optional[str]
    size: Optional[str]
    format: Optional[str]


class CivitFile_(TypedDict):
    id: int
    sizeKB: float
    name: str
    type: str
    metadata: CivitFileMetadata
    pickleScanResult: str
    pickleScanMessage: Optional[str]
    virusScanResult: str
    virusScanMessage: Optional[str]
    scannedAt: str
    hashes: dict
    downloadUrl: str
    primary: bool


class CivitImageMetadata(TypedDict):
    hash: str
    size: int
    width: int
    height: int


class CivitImage(TypedDict):
    url: str
    nsfw: str
    width: int
    height: int
    hash: str
    type: str
    metadata: CivitImageMetadata
    availability: str


class CivitModelVersion(TypedDict):
    id: int
    modelId: int
    name: str
    createdAt: str
    updatedAt: str
    status: str
    publishedAt: str
    trainedWords: List[str]
    trainingStatus: NotRequired[Optional[str]]
    trainingDetails: NotRequired[Optional[str]]
    baseModel: str
    baseModelType: str
    earlyAccessTimeFrame: int
    description: str
    vaeId: NotRequired[Optional[int]]
    stats: CivitStats
    files: List[CivitFile_]
    images: List[CivitImage]
    downloadUrl: str


class CivitModelsGetResponse(TypedDict):
    id: int
    name: str
    description: str
    type: str
    poi: bool
    nsfw: bool
    allowNoCredit: bool
    allowCommercialUse: List[str]
    allowDerivatives: bool
    allowDifferentLicense: bool
    stats: CivitStats
    creator: CivitCreator
    tags: List[str]
    modelVersions: List[CivitModelVersion]

from ingestion.scrapling.providers.awwwards import AwwwardsProvider
from ingestion.scrapling.providers.godly import GodlyProvider
from ingestion.scrapling.providers.landbook import LandbookProvider
from ingestion.scrapling.providers.lapa_ninja import LapaNinjaProvider
from ingestion.scrapling.providers.one_page_love import OnePageLoveProvider

ALL_PROVIDERS = [
    AwwwardsProvider,
    OnePageLoveProvider,
    LandbookProvider,
    GodlyProvider,
    LapaNinjaProvider,
]

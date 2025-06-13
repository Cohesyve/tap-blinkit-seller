
from tap_blinkit_seller.streams.brands import BrandsStream
from tap_blinkit_seller.streams.category import CategoryStream
from tap_blinkit_seller.streams.invoices import InvoicesStream
from tap_blinkit_seller.streams.product import ProductStream
from tap_blinkit_seller.streams.shipment import ShipmentStream
from tap_blinkit_seller.streams.transactions import TransactionStream
from tap_blinkit_seller.streams.warehouse import WarehouseStream
from tap_blinkit_seller.streams.product import ProductStream
from tap_blinkit_seller.streams.blinkit_location_states import BlinkitLocationStateStream
from tap_blinkit_seller.streams.blinkit_location_facilities import BlinkitLocationFacilityStream
from tap_blinkit_seller.streams.payouts import PayoutStream
from tap_blinkit_seller.streams.orders import OrderStream
from tap_blinkit_seller.streams.inventory import InventoryStream

AVAILABLE_STREAMS = [
    BrandsStream,
    TransactionStream,
    CategoryStream,
    InvoicesStream,
    ShipmentStream,
    WarehouseStream,
    ProductStream,
    BlinkitLocationStateStream,
    BlinkitLocationFacilityStream,
    PayoutStream,
    OrderStream,
    InventoryStream
]

__all__ = [
    'BrandsStream',
    'TransactionStream',
    'CategoryStream',
    'InvoicesStream',
    'ShipmentStream',
    'WarehouseStream',
    'ProductStream',
    'BlinkitLocationStateStream',
    'BlinkitLocationFacilityStream',
    'PayoutStream',
    'OrderStream',
    'InventoryStream'
]

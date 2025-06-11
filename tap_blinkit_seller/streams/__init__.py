
from tap_blinkit_seller.streams.brands import BrandsStream
from tap_blinkit_seller.streams.category import CategoryStream
from tap_blinkit_seller.streams.invoices import InvoicesStream
from tap_blinkit_seller.streams.product import ProductStream
from tap_blinkit_seller.streams.shipment import ShipmentStream
from tap_blinkit_seller.streams.transactions import TransactionStream
from tap_blinkit_seller.streams.warehouse import WarehouseStream


AVAILABLE_STREAMS = [
  
    BrandsStream,
    TransactionStream,
    CategoryStream,
    InvoicesStream,
    ShipmentStream,
    WarehouseStream
]

__all__ = [
   'BrandsStream',
    'TransactionStream',
    'CategoryStream',
    'InvoicesStream',
    'ShipmentStream',
    'WarehouseStream'
]

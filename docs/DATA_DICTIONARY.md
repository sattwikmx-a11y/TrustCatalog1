# Olist data dictionary — TrustCatalog

The canonical public dataset contains nine CSVs. TrustCatalog does not assume columns that are not present in these files.

| File | Important keys / fields | TrustCatalog use |
|---|---|---|
| customers | `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` | order-to-customer relationship and optional geography |
| orders | `order_id`, `customer_id`, `order_status`, purchase/approval/carrier/delivery/estimated timestamps | temporal behavior, cancellation/unavailability, delivery delay |
| order_items | `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` | seller-product attribution and item volume |
| order_payments | `order_id`, payment fields | payment context; not used as a direct reliability label |
| order_reviews | `review_id`, `order_id`, `review_score`, review text/title fields | review deterioration context |
| products | `product_id`, category, dimensions/weight, photos | listing/product context |
| sellers | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` | seller identity/location |
| geolocation | zip prefix + lat/lng/city/state | optional geographic enrichment; not required for core risk |
| product category translation | Portuguese category → English category | dashboard-readable product categories |

## Relationships

`customers.customer_id → orders.customer_id`

`orders.order_id → order_items.order_id`

`orders.order_id → order_payments.order_id`

`orders.order_id → order_reviews.order_id`

`order_items.product_id → products.product_id`

`order_items.seller_id → sellers.seller_id`

`products.product_category_name → product_category_name_translation.product_category_name`

`customers.customer_zip_code_prefix` and `sellers.seller_zip_code_prefix` can be enriched with `geolocation.geolocation_zip_code_prefix`.

## Important limitation

The public Olist dataset does **not** contain an inventory snapshot or a direct `ghost_listing` ground-truth label. TrustCatalog therefore treats `canceled` and `unavailable` order statuses as observed fulfillment-failure signals and uses controlled behavioral degradation for the early-warning stress test. The stress-test labels are explicitly simulated.

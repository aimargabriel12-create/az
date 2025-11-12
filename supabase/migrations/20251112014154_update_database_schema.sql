/*
  # Update Database Schema for Advanced Bot

  1. Add price history table for tracking price changes
  2. Add items found log for analytics
  3. Update tracked_items with additional fields
  4. Create indexes for fast queries
  
  Changes:
  - price_history: Tracks market price changes over time
  - found_items_log: Records all items discovered
  - Indexes on frequently queried columns
*/

CREATE TABLE IF NOT EXISTS price_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id uuid REFERENCES tracked_items(id) ON DELETE CASCADE,
  market_price numeric NOT NULL,
  resell_estimate numeric NOT NULL,
  recorded_at timestamptz DEFAULT now()
);

ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS found_items_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vinted_id text NOT NULL,
  title text NOT NULL,
  price numeric NOT NULL,
  brand text,
  market_price numeric,
  profit_margin numeric,
  search_keyword text,
  found_at timestamptz DEFAULT now()
);

ALTER TABLE found_items_log ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS channel_broadcasts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id uuid REFERENCES tracked_items(id) ON DELETE CASCADE,
  channel_id bigint NOT NULL,
  message_id bigint,
  broadcasted_at timestamptz DEFAULT now(),
  was_sold boolean DEFAULT false
);

ALTER TABLE channel_broadcasts ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_tracked_items_brand ON tracked_items(brand);
CREATE INDEX IF NOT EXISTS idx_tracked_items_price ON tracked_items(price);
CREATE INDEX IF NOT EXISTS idx_tracked_items_profit ON tracked_items(profit_margin);
CREATE INDEX IF NOT EXISTS idx_tracked_items_discovered ON tracked_items(discovered_at);
CREATE INDEX IF NOT EXISTS idx_found_items_log_keyword ON found_items_log(search_keyword);
CREATE INDEX IF NOT EXISTS idx_found_items_log_timestamp ON found_items_log(found_at);
CREATE INDEX IF NOT EXISTS idx_price_history_item ON price_history(item_id);

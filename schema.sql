-- =============================================
--  ВЫПОЛНИ ЭТО В SUPABASE SQL EDITOR
--  (Project → SQL Editor → New Query)
-- =============================================

-- Таблица скам-базы
CREATE TABLE IF NOT EXISTS scam_base (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT,
    username TEXT,
    phone TEXT,
    description TEXT NOT NULL,
    proof_file_ids TEXT[],          -- массив file_id фото/видео
    report_text TEXT,               -- текст жалобы от пострадавшего
    added_at TIMESTAMPTZ DEFAULT NOW(),
    added_by_user_id BIGINT,        -- кто подал жалобу
    channel_message_id BIGINT       -- ID сообщения в канале
);

-- Таблица ожидающих жалоб (на модерации)
CREATE TABLE IF NOT EXISTS pending_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,        -- кто подал
    username TEXT,
    target_telegram_id BIGINT,
    target_username TEXT,
    target_phone TEXT,
    description TEXT NOT NULL,
    proof_file_ids TEXT[],
    proof_types TEXT[],             -- 'photo' или 'video'
    report_text TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    moderation_message_id BIGINT,   -- ID сообщения в группе модерации
    status TEXT DEFAULT 'pending'   -- pending / approved / rejected
);

-- Таблица статистики поисков (опционально)
CREATE TABLE IF NOT EXISTS search_logs (
    id BIGSERIAL PRIMARY KEY,
    searched_by BIGINT,
    query TEXT,
    found BOOLEAN,
    searched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_scam_telegram_id ON scam_base(telegram_id);
CREATE INDEX IF NOT EXISTS idx_scam_username ON scam_base(username);
CREATE INDEX IF NOT EXISTS idx_scam_phone ON scam_base(phone);
CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_reports(status);

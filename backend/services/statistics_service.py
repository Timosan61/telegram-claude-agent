import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from database.models.base import SessionLocal
from database.models.campaign import Campaign
from database.models.log import ActivityLog
from database.models.statistics import (
    CampaignStatistics, SystemStatistics, ChatStatistics, 
    UserStatistics, PerformanceMetrics
)


class StatisticsService:
    """Сервис для сбора и анализа статистики системы"""
    
    def __init__(self):
        self.start_time = time.time()
        self.api_requests_count = 0
        self.api_errors_count = 0
        self.telegram_api_calls = 0
        self.telegram_rate_limit_hits = 0
    
    def increment_api_request(self, is_error: bool = False):
        """Увеличить счетчик API запросов"""
        self.api_requests_count += 1
        if is_error:
            self.api_errors_count += 1
    
    def increment_telegram_api_call(self, is_rate_limited: bool = False):
        """Увеличить счетчик вызовов Telegram API"""
        self.telegram_api_calls += 1
        if is_rate_limited:
            self.telegram_rate_limit_hits += 1
    
    def record_performance_metric(self, metric_type: str, value: float, unit: str,
                                source: str = "system", campaign_id: Optional[int] = None,
                                chat_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Записать метрику производительности"""
        try:
            db = SessionLocal()
            
            metric = PerformanceMetrics(
                metric_type=metric_type,
                value=value,
                unit=unit,
                source=source,
                campaign_id=campaign_id,
                chat_id=chat_id,
                metadata=metadata or {}
            )
            
            db.add(metric)
            db.commit()
            
        except Exception as e:
            print(f"❌ Ошибка записи метрики производительности: {e}")
        finally:
            db.close()
    
    def collect_system_statistics(self) -> Dict[str, Any]:
        """Собрать статистику системы"""
        try:
            db = SessionLocal()
            
            # Основная статистика кампаний
            total_campaigns = db.query(Campaign).count()
            active_campaigns = db.query(Campaign).filter(Campaign.active == True).count()
            
            # Статистика логов
            total_messages = db.query(ActivityLog).count()
            total_responses = db.query(ActivityLog).filter(
                ActivityLog.status == "sent"
            ).count()
            
            # Системные метрики
            uptime_hours = (time.time() - self.start_time) / 3600
            
            # CPU и память
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            
            # Создаем запись статистики
            system_stats = SystemStatistics(
                total_campaigns=total_campaigns,
                active_campaigns=active_campaigns,
                total_messages_processed=total_messages,
                total_responses_sent=total_responses,
                system_uptime_hours=uptime_hours,
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory_mb,
                api_requests_count=self.api_requests_count,
                api_errors_count=self.api_errors_count,
                telegram_api_calls=self.telegram_api_calls,
                telegram_rate_limit_hits=self.telegram_rate_limit_hits,
                telegram_connected=True  # TODO: получать из telegram_agent
            )
            
            db.add(system_stats)
            db.commit()
            db.refresh(system_stats)
            
            return system_stats.to_dict()
            
        except Exception as e:
            print(f"❌ Ошибка сбора системной статистики: {e}")
            return {}
        finally:
            db.close()
    
    def collect_campaign_statistics(self, campaign_id: Optional[int] = None, 
                                  hours_back: int = 24) -> List[Dict[str, Any]]:
        """Собрать статистику по кампаниям"""
        try:
            db = SessionLocal()
            
            # Определяем период
            since = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Фильтр по кампании
            campaign_filter = []
            if campaign_id:
                campaign_filter.append(Campaign.id == campaign_id)
            
            # Получаем кампании
            campaigns = db.query(Campaign).filter(*campaign_filter).all()
            
            results = []
            
            for campaign in campaigns:
                # Статистика по логам
                logs_query = db.query(ActivityLog).filter(
                    ActivityLog.campaign_id == campaign.id,
                    ActivityLog.timestamp >= since
                )
                
                total_processed = logs_query.count()
                responses_sent = logs_query.filter(ActivityLog.status == "sent").count()
                responses_failed = logs_query.filter(ActivityLog.status == "failed").count()
                
                # Время ответа
                processing_times = [
                    log.processing_time_ms for log in logs_query.all()
                    if log.processing_time_ms is not None
                ]
                
                avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
                max_time = max(processing_times) if processing_times else 0
                min_time = min(processing_times) if processing_times else 0
                
                # Уникальные чаты и пользователи
                unique_chats = len(set([log.chat_id for log in logs_query.all()]))
                
                # Ключевые слова
                keywords_count = Counter([log.trigger_keyword for log in logs_query.all() if log.trigger_keyword])
                
                # Создаем запись статистики
                campaign_stats = CampaignStatistics(
                    campaign_id=campaign.id,
                    messages_processed=total_processed,
                    responses_sent=responses_sent,
                    responses_failed=responses_failed,
                    avg_response_time_ms=avg_time,
                    max_response_time_ms=max_time,
                    min_response_time_ms=min_time,
                    unique_chats_active=unique_chats,
                    keywords_triggered=dict(keywords_count)
                )
                
                db.add(campaign_stats)
                
                # Добавляем в результат
                result = campaign_stats.to_dict()
                result['campaign_name'] = campaign.name
                result['campaign_active'] = campaign.active
                results.append(result)
            
            db.commit()
            return results
            
        except Exception as e:
            print(f"❌ Ошибка сбора статистики кампаний: {e}")
            return []
        finally:
            db.close()
    
    def collect_chat_statistics(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Собрать статистику по чатам"""
        try:
            db = SessionLocal()
            
            since = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Группируем логи по чатам
            chat_data = {}
            
            logs = db.query(ActivityLog).filter(ActivityLog.timestamp >= since).all()
            
            for log in logs:
                chat_id = log.chat_id
                if chat_id not in chat_data:
                    chat_data[chat_id] = {
                        'chat_title': log.chat_title,
                        'messages': [],
                        'bot_responses': 0,
                        'users': set()
                    }
                
                chat_data[chat_id]['messages'].append(log)
                if log.status == "sent":
                    chat_data[chat_id]['bot_responses'] += 1
            
            results = []
            
            for chat_id, data in chat_data.items():
                messages = data['messages']
                
                # Анализ времени
                hours_count = defaultdict(int)
                for msg in messages:
                    if msg.timestamp:
                        hour = msg.timestamp.hour
                        hours_count[hour] += 1
                
                peak_hour = max(hours_count.items(), key=lambda x: x[1])[0] if hours_count else 0
                
                # Популярные слова (из ключевых слов)
                keywords = [msg.trigger_keyword for msg in messages if msg.trigger_keyword]
                top_keywords = [{"word": word, "count": count} 
                              for word, count in Counter(keywords).most_common(10)]
                
                # Статистика длины сообщений
                message_lengths = [len(msg.original_message or "") for msg in messages]
                avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
                
                # Создаем запись статистики
                chat_stats = ChatStatistics(
                    chat_id=chat_id,
                    chat_title=data['chat_title'],
                    messages_count=len(messages),
                    bot_responses_count=data['bot_responses'],
                    unique_users_count=len(data['users']),
                    peak_hour=peak_hour,
                    messages_per_hour=dict(hours_count),
                    top_keywords=top_keywords,
                    avg_message_length=avg_length
                )
                
                db.add(chat_stats)
                results.append(chat_stats.to_dict())
            
            db.commit()
            return results
            
        except Exception as e:
            print(f"❌ Ошибка сбора статистики чатов: {e}")
            return []
        finally:
            db.close()
    
    def get_performance_trends(self, metric_type: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Получить тренды производительности"""
        try:
            db = SessionLocal()
            
            since = datetime.utcnow() - timedelta(hours=hours_back)
            
            metrics = db.query(PerformanceMetrics).filter(
                PerformanceMetrics.metric_type == metric_type,
                PerformanceMetrics.timestamp >= since
            ).order_by(PerformanceMetrics.timestamp).all()
            
            return [metric.to_dict() for metric in metrics]
            
        except Exception as e:
            print(f"❌ Ошибка получения трендов производительности: {e}")
            return []
        finally:
            db.close()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Получить сводку для дашборда"""
        try:
            db = SessionLocal()
            
            # Последние 24 часа
            since_24h = datetime.utcnow() - timedelta(hours=24)
            
            # Основные метрики
            total_campaigns = db.query(Campaign).count()
            active_campaigns = db.query(Campaign).filter(Campaign.active == True).count()
            
            # Активность за 24ч
            logs_24h = db.query(ActivityLog).filter(ActivityLog.timestamp >= since_24h)
            messages_24h = logs_24h.count()
            responses_24h = logs_24h.filter(ActivityLog.status == "sent").count()
            failed_24h = logs_24h.filter(ActivityLog.status == "failed").count()
            
            # Успешность
            success_rate = (responses_24h / max(1, messages_24h)) * 100
            
            # Активные чаты
            active_chats = len(set([log.chat_id for log in logs_24h.all()]))
            
            # Средние времена ответа
            processing_times = [
                log.processing_time_ms for log in logs_24h.all()
                if log.processing_time_ms is not None
            ]
            avg_response_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Системные метрики
            uptime_hours = (time.time() - self.start_time) / 3600
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            return {
                "campaigns": {
                    "total": total_campaigns,
                    "active": active_campaigns,
                    "inactive": total_campaigns - active_campaigns
                },
                "activity_24h": {
                    "messages_processed": messages_24h,
                    "responses_sent": responses_24h,
                    "responses_failed": failed_24h,
                    "success_rate": round(success_rate, 2),
                    "active_chats": active_chats,
                    "avg_response_time_ms": round(avg_response_time, 2)
                },
                "system": {
                    "uptime_hours": round(uptime_hours, 2),
                    "cpu_usage_percent": cpu_percent,
                    "memory_usage_percent": memory_percent,
                    "api_requests": self.api_requests_count,
                    "api_errors": self.api_errors_count,
                    "telegram_api_calls": self.telegram_api_calls
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения сводки дашборда: {e}")
            return {}
        finally:
            db.close()
    
    def get_historical_data(self, days_back: int = 7) -> Dict[str, Any]:
        """Получить исторические данные"""
        try:
            db = SessionLocal()
            
            since = datetime.utcnow() - timedelta(days=days_back)
            
            # Дневная статистика
            daily_stats = []
            for i in range(days_back):
                day_start = datetime.utcnow() - timedelta(days=i+1)
                day_end = datetime.utcnow() - timedelta(days=i)
                
                day_logs = db.query(ActivityLog).filter(
                    ActivityLog.timestamp >= day_start,
                    ActivityLog.timestamp < day_end
                )
                
                messages = day_logs.count()
                responses = day_logs.filter(ActivityLog.status == "sent").count()
                
                daily_stats.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "messages_processed": messages,
                    "responses_sent": responses,
                    "success_rate": round((responses / max(1, messages)) * 100, 2)
                })
            
            # Почасовая статистика за последние 24 часа
            hourly_stats = []
            for i in range(24):
                hour_start = datetime.utcnow() - timedelta(hours=i+1)
                hour_end = datetime.utcnow() - timedelta(hours=i)
                
                hour_logs = db.query(ActivityLog).filter(
                    ActivityLog.timestamp >= hour_start,
                    ActivityLog.timestamp < hour_end
                )
                
                messages = hour_logs.count()
                responses = hour_logs.filter(ActivityLog.status == "sent").count()
                
                hourly_stats.append({
                    "hour": hour_start.strftime("%H:00"),
                    "messages_processed": messages,
                    "responses_sent": responses
                })
            
            return {
                "daily_stats": list(reversed(daily_stats)),
                "hourly_stats": list(reversed(hourly_stats))
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения исторических данных: {e}")
            return {"daily_stats": [], "hourly_stats": []}
        finally:
            db.close()


# Глобальный экземпляр сервиса статистики
statistics_service = StatisticsService()
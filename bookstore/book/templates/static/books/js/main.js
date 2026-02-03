/* Кастомные стили для улучшения UX */
.book-card {
    transition: transform 0.3s, box-shadow 0.3s;
}

.book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.rating-stars {
    color: #ffc107;
    letter-spacing: 2px;
}

.price-tag {
    font-weight: bold;
    color: #28a745;
}

.genre-badge {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
}

.stat-card {
    border-left: 4px solid #007bff;
}

.table-hover tbody tr:hover {
    background-color: rgba(0,123,255,0.05);
}

/* Анимации */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

/* Адаптивные таблицы */
@media (max-width: 768px) {
    .table-responsive {
        font-size: 0.9rem;
    }

    .table th, .table td {
        padding: 0.5rem;
    }
}
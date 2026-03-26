import storage

events = [
    {
        "time": "09:30",
        "currency": "USD",
        "importance": 3,
        "event": "Índice de Preços ao Consumidor (IPC) - Mensal",
        "actual": "0,3%",
        "forecast": "0,2%",
        "previous": "0,1%"
    },
    {
        "time": "11:00",
        "currency": "USD",
        "importance": 3,
        "event": "Relatório de Emprego Payroll (Nonfarm)",
        "actual": "250K",
        "forecast": "180K",
        "previous": "200K"
    },
    {
        "time": "15:00",
        "currency": "USD",
        "importance": 3,
        "event": "Decisão da Taxa de Juros do FED",
        "actual": "5,50%",
        "forecast": "5,50%",
        "previous": "5,50%"
    }
]

if __name__ == "__main__":
    storage.init_db()
    storage.save_events(events)
    print("Dados fictícios (mock) adicionados no banco de dados para testes da IA.")

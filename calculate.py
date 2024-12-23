import mysql.connector

# 設定利率
i = 0.02
v = 1 / (1 + i)
d = i / (1 + i)

# 定義計算 t_Ex 的函數
def calculate_t_Ex(start_age, t, data):
    survival_probability = 1
    for year in range(t):
        current_age = start_age + year
        mortality_rate = next((float(rate) for age, rate in data if (age == "85+" and current_age >= 85) or (age.isdigit() and int(age) == current_age)), None)
        if mortality_rate is None:
            return None
        survival_probability *= (1 - mortality_rate)
    return survival_probability * (v ** t)

# 定義計算 Ax:t 的函數
def calculate_Ax_t(start_age, t, data):
    survival_probability = 1
    Ax_t = 0
    for year in range(1, t + 1):
        current_age = start_age + year - 1
        mortality_rate = next((float(rate) for age, rate in data if (age == "85+" and current_age >= 85) or (age.isdigit() and int(age) == current_age)), None)
        if mortality_rate is None:
            return None
        if year < t:
            Ax_t += survival_probability * mortality_rate * (v ** year)
            survival_probability *= (1 - mortality_rate)
        else:
            Ax_t += survival_probability * (v ** year)
    return Ax_t

# 定義計算 :ax:t 的函數
def calculate_a_x_t(Ax_t):
    return (1 - Ax_t) / d if Ax_t is not None else None

# 定義資料庫連接函數
def get_premium(age, duration, payment_duration, insurance_amount, table):
    mydb = mysql.connector.connect(
        host="localhost",
        user="tim",
        password="887414",
        database="LifeTableDB"
    )

    mycursor = mydb.cursor()
    query = f"SELECT 年齡, 死亡機率 FROM {table}"
    mycursor.execute(query)
    rows = mycursor.fetchall()

    # 計算 t_Ex, Ax:t, a_x:t
    dur_Ax_t = calculate_Ax_t(age, duration, rows)
    pay_Ax_t = calculate_Ax_t(age, payment_duration, rows)
    pay_ax_t = calculate_a_x_t(pay_Ax_t)

    # 計算保費
    premium = insurance_amount * dur_Ax_t / pay_ax_t if pay_ax_t is not None else None

    mycursor.close()
    mydb.close()

    return premium

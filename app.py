from flask import Flask, render_template, request
import requests
import pandas as pd

app = Flask(__name__)

# ---- API Configuration ----
BASE_URL = "https://www.microburbs.com.au/report_generator/api/suburb"
HEADERS = {"Authorization": "Bearer test", "Content-Type": "application/json"}

ENDPOINTS = {
    "properties": "properties",
    "demographics": "demographics",
    "schools": "schools",
    "amenities": "amenity",
    "development": "development",
    "ethnicity": "ethnicity",
    "pocket": "pocket",

}


# ---- Main Route ----
@app.route("/", methods=["GET", "POST"])
def index():
    suburb = request.form.get("suburb", "Belmont North")
    endpoint = request.form.get("endpoint", "properties")

    url = f"{BASE_URL}/{ENDPOINTS[endpoint]}"
    params = {"suburb": suburb}

    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            error=f"Error fetching data: {e}",
        )

    # ------------------------------------------------
    # 🏠 For Sale Properties Mode
    # ------------------------------------------------
    if endpoint == "properties":
        listings = data.get("results", [])
        if not listings:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No properties found."
            )

        df = pd.json_normalize(listings)
        df["address"] = df["address.street"] + ", " + df["address.sal"] + ", " + df["address.state"]
        df["price"] = df["price"].astype(float)

        avg_price = df["price"].mean()
        median_bedrooms = df["attributes.bedrooms"].median()
        common_type = df["property_type"].mode()[0]

        summary = (
            df.groupby("property_type")["price"]
            .mean()
            .reset_index()
            .rename(columns={"price": "avg_price"})
        )

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            properties=df.to_dict(orient="records"),
            summary=summary.to_dict(orient="records"),
            avg_price=round(avg_price, 0),
            median_bedrooms=int(median_bedrooms),
            common_type=common_type,
        )

    # ------------------------------------------------
    # 🎓 Schools Mode
    # ------------------------------------------------
    elif endpoint == "schools":
        results = data.get("results", [])
        if not results:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No schools found."
            )

        df = pd.DataFrame(results)
        df = df[
            [
                "name",
                "school_level_type",
                "school_sector_type",
                "gender",
                "attendance_rate",
                "naplan",
                "naplan_rank",
                "socioeconomic_rank",
            ]
        ]

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            schools=df.to_dict(orient="records"),
        )
        # ------------------------------------------------
    # 🧭 Amenities Mode
    # ------------------------------------------------
    elif endpoint == "amenities":
        results = data.get("results", [])
        if not results:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No amenities found."
            )

        df = pd.DataFrame(results)
        # Replace empty names for readability
        df["name"] = df["name"].replace("", "(Unnamed)")

        # Count how many of each category type
        summary = df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=False)

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            amenities=df.to_dict(orient="records"),
            summary=summary.to_dict(orient="records"),
        )

    # ------------------------------------------------
    # 👨‍👩‍👧‍👦 Demographics Mode
    # ------------------------------------------------
    elif endpoint == "demographics":
        age_data = pd.DataFrame(data.get("age_brackets", []))
        income_data = pd.DataFrame(data.get("income", []))
        pop_data = pd.DataFrame(data.get("population", []))

        # Filter useful subsets
        age_summary = (
            age_data[age_data["gender"] == "persons"][["age", "proportion"]]
            .query("age != 'Total'")
            .reset_index(drop=True)
        )

        income_summary = income_data[["income_bracket", "proportion"]]
        pop_summary = pop_data[["date", "value"]].sort_values("date")

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            age_summary=age_summary.to_dict(orient="records"),
            income_summary=income_summary.to_dict(orient="records"),
            pop_summary=pop_summary.to_dict(orient="records"),
        )
        # ------------------------------------------------
    # 🏗️ Development Mode
    # ------------------------------------------------
    elif endpoint == "development":
        results = data.get("results", [])
        if not results:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No development data found."
            )

        df = pd.DataFrame(results)

        # Group by category for chart
        summary = df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=False)

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            development=df.to_dict(orient="records"),
            summary=summary.to_dict(orient="records"),
        )
        # ------------------------------------------------
    # 🌏 Ethnicity Mode
    # ------------------------------------------------
    elif endpoint == "ethnicity":
        results = data.get("results", [])
        if not results:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No ethnicity data found."
            )

        # Flatten nested dictionaries
        df = pd.json_normalize(results, sep="_")
        # Combine all ethnicity proportions across areas
        ethnicity_cols = [c for c in df.columns if c.startswith("ethnicity_")]
        mean_values = df[ethnicity_cols].mean().sort_values(ascending=False).reset_index()
        mean_values.columns = ["ethnicity", "proportion"]
        mean_values["ethnicity"] = mean_values["ethnicity"].str.replace("ethnicity_", "")

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            ethnicity_data=mean_values.to_dict(orient="records"),
        )

        # ------------------------------------------------
    # 💰 Pocket Prices Mode
    # ------------------------------------------------
    elif endpoint == "pocket":
        results = data.get("results", [])
        if not results or not isinstance(results, list) or len(results) < 2:
            return render_template(
                "index.html", suburb=suburb, endpoint=endpoint, error="No pocket price data found."
            )

        # Each element in results is a list: one for houses, one for units
        house_data = results[0]
        unit_data = results[1]

        # Convert to DataFrames
        df_house = pd.DataFrame(house_data)
        df_unit = pd.DataFrame(unit_data)

        # Compute average price and growth for both types
        house_summary = {
            "avg_price": round(df_house["value"].mean(), 0),
            "avg_growth": round(df_house["growth"].dropna().mean(), 2),
        }
        unit_summary = {
            "avg_price": round(df_unit["value"].mean(), 0),
            "avg_growth": round(df_unit["growth"].dropna().mean(), 2),
        }

        # Combine summary for chart
        price_summary = pd.DataFrame([
            {"property_type": "House", **house_summary},
            {"property_type": "Unit", **unit_summary}
        ])

        return render_template(
            "index.html",
            suburb=suburb,
            endpoint=endpoint,
            house_data=df_house.to_dict(orient="records"),
            unit_data=df_unit.to_dict(orient="records"),
            price_summary=price_summary.to_dict(orient="records"),
        )


    # ------------------------------------------------
    # Fallback
    # ------------------------------------------------
    else:
        return render_template("index.html", suburb=suburb, endpoint=endpoint, rawdata=data)


if __name__ == "__main__":
    app.run(debug=True)

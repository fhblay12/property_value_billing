import plotly.graph_objs as go
import plotly.io as pio


class Admin_home_service:

        def __init__(self, admin_home_repository):
            self.admin_home_repository = admin_home_repository
            
        def get_category_counts(self):
                  labels=["Residential", "Commercial"]
                  data = self.admin_home_repository.get_category_counts()
                  categories = [row[0] for row in data]
                  counts = [row[1] for row in data]
                      # Create Pie chart using Plotly
                  fig = go.Figure(data=[go.Pie(labels=labels, values=counts, hole=0.3)])
                  fig.update_layout(
                        title=dict(
                            text="Property category",
                            font=dict(
                                size=20,
                                color="#000000",
                                family="Arial Black"  # ✅ bold
                            )
                        ),
                        paper_bgcolor="#668cff",  # outside chart
                        plot_bgcolor="#668cff",
                        font=dict(color="#000000"),
                    )
                  return {"categories": categories, "counts": counts, "fig": fig}
                        
        def get_city_counts(self):
                  data = self.admin_home_repository.get_city_counts()
                  cities = [row[0] for row in data]
                  counts = [row[1] for row in data]
                  
                  fig2 = go.Figure(data=[go.Pie(labels=cities, values=counts, hole=0.3)])
                  fig2.update_layout(
                    title=dict(
                        text="Property cities",
                        font=dict(
                            size=20,
                            color="#000000",
                            family="Arial Black"  # ✅ bold
                        )
                    ),
                    paper_bgcolor="#668cff",  # outside chart
                    plot_bgcolor="#668cff",
                    font=dict(color="#000000"),
                )
                  return {"cities": cities, "counts": counts, "fig": fig2}
        
        def property_count_today(self):
            return self.admin_home_repository.property_count_today()
        
        def contact_count_today(self):
            return self.admin_home_repository.contact_count_today()
        
        def property_count(self):
            return self.admin_home_repository.property_count()
        
        def expected_monthly_revenue(self):
            return self.admin_home_repository.expected_monthly_revenue()
        
        def total_revenue_collected(self):
            return self.admin_home_repository.total_revenue_collected()
        
        def revenue_by_payment_date(self):
            rows = self.admin_home_repository.revenue_by_payment_date()
            date_strings = [row[0].date().isoformat() for row in rows]
            revenue = [row[1] for row in rows]


            # Create Plotly line chart
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=date_strings,
                y=revenue,
                name='Revenue',

            ))

            # Dark theme
            fig3.update_layout(
            title=dict(
                text="Daily Revenue",
                font=dict(
                    size=20,
                    color="#000000",
                    family="Arial Black"  # ✅ bold
                )
            ),
            paper_bgcolor="#668cff",
            plot_bgcolor="#668cff",
            font=dict(color="#000000"),
            )

            # Convert to HTML div for FastAPI template
            chart_html = pio.to_html(fig3, full_html=False)
            return {"date_strings": date_strings, "revenue": revenue, "chart_html": chart_html}
                
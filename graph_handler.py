import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class graph_handler:
    
    def create_total_post_chart(self, users):
        
        labels = None
        posts = []

        first_loop = True

        for user in users:

            posts.append(user[3])

            if first_loop:
                labels = (user[1],)
                first_loop = False
            else:
                labels = labels + (user[1],)
        
        p, tx, autotexts = plt.pie(posts, labels=labels, autopct="", shadow=True, startangle=90)

        for i, a in enumerate(autotexts):
            a.set_text("{}".format(posts[i]))


        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.savefig("./charts/Total Posts Chart.png", bbox_inches='tight')

    def create_total_bangers_chart(self):
        #Todo
        return

    
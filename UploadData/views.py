import csv, io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import uuid
from datetime import datetime
from django.http import HttpResponseRedirect


def data_upload(request):
    data = controller_data.objects.all()
    prompt = {"data": data}

    if request.method == "GET":
        return render(request, "upload.html", prompt)

    csv_file = request.FILES.get("file", False)
    if not csv_file:
        messages.error(request, "Please select the file")
        return redirect("/upload")

    elif not csv_file.name.endswith("csv"):
        messages.error(request, "Not a csv file")
        return redirect("/upload")
    else:
        data_set = csv_file.read().decode("UTF-8")
        io_string = io.StringIO(data_set)
        next(io_string)
        data_list = []
        file_id = uuid.uuid4()
        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            row_data = controller_data(
                ego_speed=column[0],
                leader_speed=column[1],
                space_gap=column[2],
                accel=column[3],
                file_id=file_id,
            )

            file_record = controller_file(
                file_id=file_id, file_name=csv_file, upload_time=datetime.now()
            )
            data_list.append(row_data)
        file_record.save()
        controller_data.objects.bulk_create(data_list)
        # messages.success(request,"data uploaded")
        return redirect("/data-list")


def get_all_files(request):
    files = controller_file.objects.order_by("-upload_time")
    return render(request, "data-list.html", {"files": files})


# delete the data and file object based on file_id
def delete_file(request, fid):
    rm_file = controller_file.objects.get(file_id=fid)
    rm_file.delete()
    rm_data = controller_data.objects.filter(file_id=fid)
    rm_data.delete()
    return redirect("/data-list")

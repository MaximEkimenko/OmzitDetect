let start = document.getElementById('inputStartTime');
let end = document.getElementById('inputEndTime');
let timeLine = document.getElementById('timeline');
let formIntervals = document.getElementById('intervalsInput');

let merged_time_intervals = ''

document.getElementById("addInterval").onclick = function() {
   console.log(merged_intervals)
   let interval = []
   interval.push(convertTimeToMinutes(start.value))
   interval.push(convertTimeToMinutes(end.value))
   merged_intervals.push(interval)
   merged_intervals = merge(merged_intervals)
   intervalsToTimeLine(merged_intervals)
};

document.addEventListener('click', handleClick)

function handleClick (event) {
    if (event.srcElement.id.includes('delbtn')) {
        let id = event.srcElement.id.split('-')
        delete_Interval(Number(id[1]))
        event.srcElement.offsetParent.remove()
    }
}

function delete_Interval(n) {
  console.log(n)
  merged_intervals.splice(n, 1)
  intervalsToTimeLine(merged_intervals)
}

function intervalsToTimeLine (merged_intervals) {
    const minutesInDay = 1440
    let lastPointEndMinute = 0
    timeLine.innerHTML = ''
    merged_time_intervals = ''
    for (let i = 0; i < merged_intervals.length; i++) {
        let startMinute = merged_intervals[i][0]
        let endMinute = merged_intervals[i][1]
        let emptyInterval = Math.round((startMinute - lastPointEndMinute) / 14.4)
        lastPointEndMinute = endMinute
        let fillInterval = Math.round((endMinute - startMinute) / 14.4)

        startTime = convertMinutesToTime(startMinute)
        endTime = convertMinutesToTime(endMinute)
        merged_time_intervals += startTime + '-' + endTime + ','

        let deleteButton = createElementFromHTML(`
            <div class="btn btn-danger btn-sm" id="delbtn-${i}">Delete</div>
        `)

        timeLine.innerHTML += `
            <span class="progress-bar" style="width: ${emptyInterval}%; background-color: #eaecf4"
                  aria-valuenow="${emptyInterval}" aria-valuemin="0" aria-valuemax="100"
            ></span>
            <span class="bg-success example-popover" style="width: ${fillInterval}%"
                  aria-valuenow="${fillInterval}" aria-valuemin="0" aria-valuemax="100"
                  data-container="body" data-toggle="popover" data-placement="top" data-html="true"
                  data-content='
                    <span class="mr-2">${startTime}-${endTime}</span>
                    ${deleteButton.outerHTML}
                  '
            ></span>
        `
    }
    $(function popoverUpdate () {
        $('[data-toggle="popover"]').popover()
   })
   formIntervals.value = merged_time_intervals
   console.log(formIntervals.value)
}


function createElementFromHTML(htmlString) {
  var div = document.createElement('div');
  div.innerHTML = htmlString.trim();

  return div.firstChild;
}

function convertTimeToMinutes (time) {
   let a = time.split(':');
   return (+a[0]) * 60 + (+a[1]);
}

function convertMinutesToTime (mins) {
    let hours = Math.trunc(mins/60);
    let minutes = mins % 60;
    if (minutes < 10) {
        minutes = '0' + minutes
    }
    return hours + ':' + minutes;
}

const merge = (intervals) => {
  if (intervals.length < 2) {
    return intervals
  }

  const sortedIntervals = intervals.sort((a, b) => a[0] - b[0])

  const result = [sortedIntervals[0]]

  for (let i = 0; i < sortedIntervals.length; i++) {
    let lastEnd = result[result.length - 1][1]

    let current = intervals[i]
    let currentStart = current[0]
    let currentEnd = current[1]

    if (currentStart <= lastEnd) {
      result[result.length - 1][1] = Math.max(lastEnd, currentEnd)
    } else {
      result.push(current)
    }
  }
  return result
}
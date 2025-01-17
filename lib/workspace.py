from string import Template

from lib.file.extra import amplitude as amp


class Workspace:
    def __init__(self, utc_time_func):
        """
        Class to realize results and its output
        :type utc_time_func: function object from DrumCorr to search value using UTCDateTime
        """
        self.values = {}
        self.get_time_value = utc_time_func

        self.current_file_name = None
        self.detection_value = None
        self.approx_xcorr = None

        self.max_amp_xcorr = None
        self.max_amp_val = None
        self.max_amp_time = None

        # anon functions
        self.stream = None
        # self.values['chars'] = None  # characteristics dictionary
        # self.amplitude_multiplier = None  # convert to actual amplitude data
        self.detects = None
        self.sims = None
        self.times = None

        # config vars
        self.time_format = "%Y-%m-%d\t%H:%M:%S"
        self.time_little_format = "%H:%M:%S"

    def format_delta_str_out(self, delta_obj):
        """
        Timedelta format without milliseconds
        :param delta_obj:
        :return:
        """

        class DeltaTemplate(Template):
            delimiter = "%"

        d = {"D": delta_obj.days}
        d["H"], rem = divmod(delta_obj.seconds, 3600)
        d["M"], d["S"] = divmod(rem, 60)
        t = DeltaTemplate(self.time_little_format)
        return t.substitute(**d)

    def report_head(self):
        out = '''DrumCorr File <{file}> result:\n
Beats count:\t\t\t{beats}
Detection value:\t\t{detect}
Average correlation:\t{xcorr:0.3f}
Average amplitude:\t\t{aver_amp:0.2f}
Average amp delta:\t\t{aver_delta}
Max corr:
    Value:\t\t{max_amp_c:0.3f}
    Amplitude:\t{max_amp_v:0.2f}
    Amp time:\t{max_amp_t}'''.format(file=self.current_file_name,
                                     beats=len(self.detects),
                                     detect=self.detection_value,
                                     xcorr=self.approx_xcorr,
                                     max_amp_c=self.max_amp_xcorr,
                                     max_amp_v=self.max_amp_val,
                                     max_amp_t=self.max_amp_time,
                                     aver_amp=amp.average_amplitude(self.detects),
                                     aver_delta=self.format_delta_str_out(
                                         amp.average_delta_time(self.detects))
                                     )
        return out

    def report_print(self):
        print(self.report_head())

    def report_to_file(self, out_file_name, experimental=False):
        """
        Writing report to file
        :param experimental: enable experimental futures
        :type out_file_name: name of output report file
        """
        # find max amplitude values
        #
        self.max_amp_xcorr = max([i['similarity'] for i in self.detects])
        for detect in self.detects:
            if detect['similarity'] == self.max_amp_xcorr:
                self.max_amp_val = detect['max_amplitude']  # amp.return_micron_to_seconds(detect['max_amplitude'])
                self.max_amp_time = detect['max_amplitude_time'].strftime(self.time_format)
        #
        # #

        # make output
        #
        with open(out_file_name, 'w+') as f:
            #  export header with results
            f.write(self.report_head())

            # write space
            f.write('\n\n')

            #  out data
            for detect in self.detects:
                cur_time = detect['time'].datetime.strftime(self.time_format)
                #  set experimental calc amplitude
                if experimental:
                    amp_calc = detect['max_amplitude']  # amp.return_micron_to_seconds(detect['max_amplitude'])
                else:
                    # set skip amplitude calc
                    amp_calc = 0
                #  write data
                f.write('{current_time}\t{sim:0.3f}\t{amp:0.2f}\n'.format(current_time=str(cur_time),
                                                                          sim=detect['similarity'],
                                                                          amp=amp_calc)
                        )

            f.close()
        #
        # #

    def generate_report_name(self, report_format):
        return report_format.format(file_name=self.current_file_name)
